/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./assets/scripts/index.js":
/*!*********************************!*\
  !*** ./assets/scripts/index.js ***!
  \*********************************/
/***/ (() => {

eval("$( document ).ready(function() {\r\n\r\n    $('#like-form').submit(function(e){\r\n        e.preventDefault()\r\n\r\n        const post_id = $(this).attr('elementID')\r\n        const url = $(this).attr('action')\r\n\r\n        $.ajax({\r\n            type: 'POST',\r\n            url: url,\r\n            data: {\r\n                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),\r\n                'post_id':post_id,\r\n            },\r\n            dataType: 'json',\r\n            success: function(response) {\r\n                $(`#likes_count${post_id}`).text(response['amount_likes'])\r\n            },\r\n\r\n            error: function(response) {\r\n                alert('An error has occurred while liking a post!')\r\n            }\r\n        })\r\n\r\n    })\r\n});\r\n\n\n//# sourceURL=webpack://task-14---add-a-little-look/./assets/scripts/index.js?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = {};
/******/ 	__webpack_modules__["./assets/scripts/index.js"]();
/******/ 	
/******/ })()
;