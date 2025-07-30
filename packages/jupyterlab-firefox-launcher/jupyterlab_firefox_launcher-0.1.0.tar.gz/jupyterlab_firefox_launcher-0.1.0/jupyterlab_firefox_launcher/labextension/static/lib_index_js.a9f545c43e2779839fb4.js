"use strict";
(self["webpackChunkjupyterlab_firefox_launcher"] = self["webpackChunkjupyterlab_firefox_launcher"] || []).push([["lib_index_js"],{

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
// src/handler.ts
/**
 * Make a request to the backend of the JupyterLab Firefox launcher extension.
 *
 * This helper wraps a `fetch` call to a Jupyter server extension API endpoint.
 *
 * @param endpoint - The endpoint to call (e.g., 'launch')
 * @param init - The fetch initialization parameters
 * @returns A promise resolving to the response JSON
 */
async function requestAPI(endpoint = '', init = {}) {
    const url = `/jupyterhub-firefox-launcher/${endpoint}`;
    const response = await fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json'
        },
        ...init
    });
    if (!response.ok) {
        const message = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${message}`);
    }
    return response.json();
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler.js */ "./lib/handler.js");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_3__);




const buildFirefoxHTML = (iframeId, url) => {
    return `
    <div style="display:flex; justify-content:end; padding:4px; gap:8px; background:#f5f5f5;">
      <button id="ff-refresh">🔄 Refresh</button>
      <button id="ff-fullscreen">⛶ Fullscreen</button>
      <button id="ff-close">❌ Close</button>
    </div>
    <iframe 
      id="${iframeId}"
      src="${url}" 
      style="width:100%; height:90%; border:none;"
      allowfullscreen
    ></iframe>`;
};
const requestFullscreen = (element) => {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    }
    else if (element.webkitRequestFullscreen) {
        element.webkitRequestFullscreen();
    }
    else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    }
    else if (element.msRequestFullscreen) {
        element.msRequestFullscreen();
    }
};
const handleFullscreenChange = () => {
    if (!document.fullscreenElement &&
        !document.webkitFullscreenElement &&
        !document.mozFullScreenElement &&
        !document.msFullscreenElement) {
        console.log('Exited fullscreen mode');
    }
};
const extension = {
    id: 'jupyterlab-firefox-launcher:plugin',
    description: 'JupyterLab extension to launch Firefox in a tab',
    autoStart: true,
    requires: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_0__.ILauncher, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette],
    activate: async (app, launcher, palette) => {
        const command = 'firefox:open';
        const label = 'Firefox Browser';
        const url = 'http://localhost:6080';
        app.commands.addCommand(command, {
            label,
            execute: async () => {
                var _a, _b, _c;
                // Request the backend to launch Firefox
                try {
                    await (0,_handler_js__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('launch');
                }
                catch (e) {
                    console.error('Failed to launch Firefox:', e);
                }
                const content = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_3__.Widget();
                content.node.style.height = '100%';
                content.node.style.width = '100%';
                content.node.style.overflow = 'hidden';
                const iframeId = 'firefox-iframe';
                content.node.innerHTML = buildFirefoxHTML(iframeId, url);
                const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
                widget.id = 'firefox-browser';
                widget.title.label = label;
                widget.title.closable = true;
                widget.node.style.height = '100%';
                app.shell.add(widget, 'main');
                app.shell.activateById(widget.id);
                const iframe = content.node.querySelector(`#${iframeId}`);
                if (!iframe) {
                    console.error('Firefox iframe not found');
                    return;
                }
                (_a = content.node.querySelector('#ff-refresh')) === null || _a === void 0 ? void 0 : _a.addEventListener('click', () => {
                    iframe.src = iframe.src;
                });
                (_b = content.node.querySelector('#ff-close')) === null || _b === void 0 ? void 0 : _b.addEventListener('click', () => {
                    widget.close();
                });
                (_c = content.node.querySelector('#ff-fullscreen')) === null || _c === void 0 ? void 0 : _c.addEventListener('click', () => {
                    requestFullscreen(iframe);
                });
                // Auto exit fullscreen on ESC key
                document.addEventListener('fullscreenchange', handleFullscreenChange);
                document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
                document.addEventListener('mozfullscreenchange', handleFullscreenChange);
                document.addEventListener('MSFullscreenChange', handleFullscreenChange);
            }
        });
        launcher.add({
            command,
            category: 'Other',
            rank: 1
        });
        palette.addItem({
            command,
            category: 'Firefox'
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (extension);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.a9f545c43e2779839fb4.js.map