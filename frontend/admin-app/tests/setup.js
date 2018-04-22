// Tests are placed alongside files under test.
// This file does the following:
// 1. Sets the environment to 'production' so that
//    dev-specific babel config in .babelrc doesn't run.
// 2. Disables Webpack-specific features that Mocha doesn't understand.
// 3. Registers babel for transpiling our code for testing.

// Disable webpack-specific features for tests since
// Mocha doesn't know what to do with them.
require.extensions['.css'] = function () {
    return null;
};
require.extensions['.png'] = function () {
    return null;
};
require.extensions['.jpg'] = function () {
    return null;
};

// Register babel so that it will transpile ES6 to ES5
// before our tests run.
require('babel-register')();


import Adapter from 'enzyme-adapter-react-16'
import Enzyme from 'enzyme'
import {expect, describe, it, beforeEach, afterEach} from 'chai'
import jQuery from 'jquery'
import jsdom from 'jsdom'

Enzyme.configure({ adapter: new Adapter() , transform: {"^.+\\.jsx?$": "babel-jest"}})

function exposeChaiGlobally() {
    global.afterEach = afterEach
    global.beforeEach = beforeEach
    global.describe = describe
    global.expect = expect
    global.it = it
}

exposeChaiGlobally()


function initializeBrowser() {
    const { JSDOM } = jsdom
    const dom = new JSDOM('<!doctype html><html><body></body></html>', {url: 'https://python.clinic/'})
    const { window } = dom
    const jq = jQuery(window)

    global.window = window
    global.document = window.document
    global.navigator = {
        userAgent: 'node.js',
    }

    global.jQuery = jq
    global.$ = jq
    copyProps(window, global)
}

function copyProps(src, target) {
    const props = Object.getOwnPropertyNames(src)
                        .filter(prop => typeof target[prop] === 'undefined')
                        .map(prop => Object.getOwnPropertyDescriptor(src, prop))
    Object.defineProperties(target, props)
}
initializeBrowser()
