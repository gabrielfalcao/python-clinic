import 'react-notifications/lib/notifications.css'
import 'bulma/css/bulma.css'

import React from "react"
import PropTypes from 'prop-types'

import ReactDOM from 'react-dom'
import * as Redux from 'react-redux'
import { createStore, applyMiddleware } from 'redux'
import { routerMiddleware } from 'react-router-redux'
import { compose } from 'redux'


import registerServiceWorker from 'python-clinic/registerServiceWorker'

import App from 'python-clinic/App'
import PythonClinicApplication from 'python-clinic/reducers'
import {history} from 'python-clinic/utils/history'
import { save, load } from "redux-localstorage-simple"
import {PythonClinicReduxHttpClient} from 'python-clinic/networking'


const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose
const store = createStore(PythonClinicApplication, load({namespace: 'pythonclinic.state'}), composeEnhancers(
    applyMiddleware(
        routerMiddleware(history),
        save({namespace: 'pythonclinic.state'}),
    )
))

class ApiProvider extends React.Component {
    static childContextTypes = {
        api: PropTypes.object,
    }
    static propTypes = {
        store: PropTypes.object.isRequired,
    }
    getChildContext = () => {
        return {
            api: new PythonClinicReduxHttpClient(this.props.store)
        }
    }
    render() {
        return this.props.children
    }
}

ReactDOM.render(
    <Redux.Provider store={store}>
        <ApiProvider store={store}>
            <App />
        </ApiProvider>
    </Redux.Provider>,
    document.getElementById('root')
)
registerServiceWorker()
