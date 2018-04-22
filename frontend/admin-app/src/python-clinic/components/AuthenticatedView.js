import React from "react"
import PropTypes from 'prop-types'
import { Redirect, withRouter } from "react-router-dom"
/* import {NotificationManager} from 'react-notifications'*/

import {ComponentWithStore} from 'python-clinic/utils/ui'
import {auth_is_active} from 'python-clinic/utils/auth'


class AuthenticatedView extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static defaultProps = {
        auth: {},
        loginPath: '/admin/login',
        noRedirect: false,
        location: {}
    }
    static propTypes = {
        auth: PropTypes.object.isRequired,
        location: PropTypes.object,
        loginPath: PropTypes.string,
        noRedirect: PropTypes.bool,
    }
    render() {
        const {props} = this
        const {children, loginPath, noRedirect, auth} = props

        if (auth_is_active(auth)) {
            return children
        }
        /* else {
         *   NotificationManager.warning(`The token has expired`, `Authentication Required`)
         * }
         */

        if (noRedirect) {
            return null
        }

        return <Redirect to={loginPath}/>

    }
}


export default ComponentWithStore(withRouter(AuthenticatedView))
