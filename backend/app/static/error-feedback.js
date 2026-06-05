/**
 * ErrHub Error Feedback SDK
 *
 * 在 HTML 中引入即可使用：
 *   <script src="https://your-domain/sdk/error-feedback.js" data-api-token="your-token"></script>
 *
 * 手动上报：
 *   ErrHub.report('TypeError', 'something went wrong', { severity: 'error' })
 *
 * 自动捕获未处理异常（默认开启）：
 *   <script src="..." data-api-token="..." data-auto-capture="true"></script>
 */
(function () {
  'use strict';

  // ---- 从 script 标签读取配置 ----
  var script = document.currentScript;
  if (!script) {
    // fallback: 查找最后一个匹配的 script 标签
    var scripts = document.getElementsByTagName('script');
    for (var i = scripts.length - 1; i >= 0; i--) {
      if (scripts[i].src && scripts[i].src.indexOf('error-feedback') !== -1) {
        script = scripts[i];
        break;
      }
    }
  }

  if (!script) {
    console.error('[ErrHub] SDK script tag not found.');
    return;
  }

  var apiToken = script.getAttribute('data-api-token') || '';
  var autoCapture = script.getAttribute('data-auto-capture') !== 'false'; // 默认 true
  var environment = script.getAttribute('data-environment') || 'production';
  var beforeSendFn = script.getAttribute('data-before-send') || ''; // window 上的回调函数名

  if (!apiToken) {
    console.error('[ErrHub] data-api-token is required on the script tag.');
    return;
  }

  // ---- 推断 API 基础地址 ----
  var scriptSrc = script.src;
  var baseUrl = scriptSrc.substring(0, scriptSrc.lastIndexOf('/sdk/'));
  var apiUrl = baseUrl + '/api/v1/errors';

  // ---- 内部状态 ----
  var _queue = [];
  var _sending = false;
  var _maxQueueSize = 50;
  var _batchInterval = null;

  /**
   * 触发 beforeSend 回调
   * - 返回 false         → 取消本次上报
   * - 不返回 / 返回 payload → 继续上报（可用修改后的 payload）
   */
  function _applyBeforeSend(payload) {
    if (!beforeSendFn) return payload;
    var fn = window[beforeSendFn];
    if (typeof fn !== 'function') return payload;
    try {
      var result = fn(payload, payload.context);
      if (result === false) return null; // 显式返回 false 取消上报
      return result || payload;          // 未返回或返回 falsy 则用原始 payload
    } catch (e) {
      console.warn('[ErrHub] beforeSend callback error:', e);
      return payload; // 回调出错时仍发送原始 payload
    }
  }

  /**
   * 发送单条错误到后端
   */
  function _send(payload) {
    try {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', apiUrl, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.setRequestHeader('X-API-Token', apiToken);
      xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status >= 400) {
          console.warn('[ErrHub] Report failed:', xhr.status, xhr.responseText);
        }
      };
      xhr.send(JSON.stringify(payload));
    } catch (e) {
      // 静默失败，不影响宿主页面
    }
  }

  /**
   * 将错误加入队列，定时批量发送
   */
  function _enqueue(payload) {
    if (_queue.length < _maxQueueSize) {
      _queue.push(payload);
    }
    if (!_batchInterval) {
      _batchInterval = setInterval(_flush, 2000);
    }
  }

  /**
   * 刷新队列，发送所有待发送的错误
   */
  function _flush() {
    if (_queue.length === 0) {
      clearInterval(_batchInterval);
      _batchInterval = null;
      return;
    }
    while (_queue.length > 0) {
      var item = _queue.shift();
      var processed = _applyBeforeSend(item);
      if (processed) _send(processed);
    }
  }

  /**
   * 将对象转为有意义的消息字符串
   * 避免 [object Response]、[object Object] 等无意义输出
   */
  function _toMessage(value) {
    if (!value) return 'Unknown error';
    if (typeof value === 'string') return value;

    // fetch API 的 Response 对象
    if (typeof Response !== 'undefined' && value instanceof Response) {
      var parts = [];
      try {
        var url = value.url;
        var method = 'GET';
        // Response 本身没有 method，但可以从 request 推断
        parts.push((method || '') + ' ' + url);
      } catch (_) { /* ignore */ }
      parts.push(value.status + ' ' + (value.statusText || ''));
      parts.push('(' + value.type + ')');
      var msg = parts.filter(Boolean).join(' ');
      return msg || 'HTTP Response Error';
    }

    // 有自定义 toString 的对象（非 Object.prototype.toString）
    if (value.toString && typeof value.toString === 'function' &&
        value.toString !== Object.prototype.toString) {
      var str = value.toString();
      if (str) return str;
    }

    // 普通对象，尝试 JSON 序列化
    try {
      var json = JSON.stringify(value);
      if (json && json !== '{}') return json;
    } catch (_) { /* ignore */ }

    return String(value);
  }

  /**
   * 格式化 Error 对象的堆栈
   */
  function _formatStack(error) {
    if (!error) return undefined;
    if (typeof error.stack === 'string') return error.stack;
    return undefined;
  }

  /**
   * 获取当前页面上下文信息
   */
  function _getPageContext() {
    return {
      url: window.location.href,
      userAgent: navigator.userAgent,
      language: navigator.language,
      referrer: document.referrer || undefined,
      viewport: window.innerWidth + 'x' + window.innerHeight,
      screen: screen.width + 'x' + screen.height,
    };
  }

  // ---- 公开 API ----

  /**
   * 上报一条错误
   *
   * @param {string} exceptionType - 异常类型，如 'TypeError'、'ValueError'
   * @param {string} message - 异常消息
   * @param {object} [options] - 可选参数
   * @param {string} [options.stackTrace] - 堆栈信息
   * @param {string} [options.severity] - 严重级别: debug/info/warning/error/critical
   * @param {string} [options.environment] - 环境: development/staging/production
   * @param {object} [options.context] - 自定义上下文 JSON 对象
   * @param {boolean} [options.immediate] - 是否立即发送（跳过队列）
   * @returns {void}
   */
  function report(exceptionType, message, options) {
    if (!exceptionType || !message) {
      console.warn('[ErrHub] exceptionType and message are required.');
      return;
    }

    options = options || {};

    var payload = {
      exception_type: exceptionType,
      message: message,
      stack_trace: options.stackTrace || undefined,
      severity: options.severity || 'error',
      environment: options.environment || environment,
      source: 'frontend',
      context: { ..._getPageContext(), ...options.context },
    };

    if (options.immediate) {
      var processed = _applyBeforeSend(payload);
      if (processed) _send(processed);
    } else {
      _enqueue(payload);
    }
  }

  /**
   * 捕获并上报一个 Error 对象或异常事件
   *
   * @param {Error|ErrorEvent|PromiseRejectionEvent} error - 错误对象
   * @param {object} [options] - 同 report 的 options
   */
  function captureException(error, options) {
    options = options || {};
    var exceptionType = 'Error';
    var message = 'Unknown error';
    var stackTrace = undefined;

    if (error instanceof Error) {
      exceptionType = error.name || 'Error';
      message = error.message || 'Unknown error';
      stackTrace = _formatStack(error);
    } else if (error instanceof ErrorEvent) {
      exceptionType = (error.error && error.error.name) || 'Error';
      message = _toMessage(error.message) || _toMessage(error.error && error.error.message) || 'Unknown error';
      stackTrace = _formatStack(error.error);
    } else if (error && typeof error === 'object') {
      // PromiseRejectionEvent
      if (error.reason) {
        if (error.reason instanceof Error) {
          exceptionType = error.reason.name || 'UnhandledRejection';
          message = error.reason.message || 'Unhandled promise rejection';
          stackTrace = _formatStack(error.reason);
        } else {
          exceptionType = 'UnhandledRejection';
          message = _toMessage(error.reason);
        }
      } else {
        exceptionType = 'UnhandledRejection';
        message = 'Unhandled promise rejection';
      }
    }

    report(exceptionType, message, {
      stackTrace: stackTrace,
      severity: options.severity || 'error',
      environment: options.environment,
      context: options.context,
      immediate: options.immediate,
    });
  }

  /**
   * 手动刷新队列，立即发送所有待发送的错误
   */
  function flush() {
    _flush();
  }

  // ---- 自动捕获 ----

  if (autoCapture) {
    // 全局未捕获异常
    window.addEventListener('error', function (event) {
      captureException(event, { severity: 'error' });
    });

    // 未处理的 Promise rejection
    window.addEventListener('unhandledrejection', function (event) {
      captureException(event, { severity: 'error' });
    });
  }

  // 页面关闭前刷新队列
  window.addEventListener('beforeunload', function () {
    _flush();
  });

  // ---- 挂载到 window ----

  var ErrHub = {
    report: report,
    captureException: captureException,
    flush: flush,
    version: '1.0.0',
  };

  window.ErrHub = ErrHub;

  // 兼容 AMD
  if (typeof define === 'function' && define.amd) {
    define(function () { return ErrHub; });
  }

  // 兼容 CommonJS
  if (typeof module === 'object' && module.exports) {
    module.exports = ErrHub;
  }

})();
