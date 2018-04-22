import React from "react"
import PropTypes from 'prop-types'

import { BrowserRouter as Router, Route, Switch, Redirect } from "react-router-dom"
/* import { NavLink } from "react-router-dom";*/
import {NotificationContainer} from 'react-notifications'

import SideBar from 'python-clinic/SideBar'
import TopBar from 'python-clinic/TopBar'
import NotFound from 'python-clinic/pages/NotFound'

import * as Project from 'python-clinic/Project'
import Welcome from 'python-clinic/pages/Welcome'
import Login from 'python-clinic/pages/Login'
import Logout from 'python-clinic/pages/Logout'
import {auth_is_active} from 'python-clinic/utils/auth'
import {ComponentWithStore} from 'python-clinic/utils/ui'


class App extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static defaultProps = {
        auth: {},
    }
    static propTypes = {
        auth: PropTypes.object,
    }
    render() {
        const {auth} = this.props
        const AuthenticatedRoute = ComponentWithStore(({ component: Component, ...rest }) => (
            <Route {...rest} render={({...props}) => (
                    auth_is_active(auth)
                    ? <Component {...{...props, ...rest}} />
                    : <Redirect to='/admin/login' />
                )} />
        ))
        return (
            <Router>
                <div>
                    <NotificationContainer />
                    <TopBar />
                    <div className="container-fluid">
                        <div className="row">
                            <SideBar />
                            <Switch>
                                {/* redirects */}
                                <Redirect from='/web' to='/admin'/>
                                <Route exact path="/" component={Welcome} />
                                <Redirect exact from='/admin' to='/admin/projects'/>
                                <Redirect exact from='/projects' to='/admin/projects'/>
                                <Redirect exact from='/login' to='/admin/login'/>
                                <Redirect exact from='/logout' to='/admin/logout'/>

                                {/* routes */}
                                <Route exact path="/admin/login" component={Login} />
                                <Route exact path="/admin/logout" component={Logout} />

                                <AuthenticatedRoute exact path="/admin/projects" component={Project.List} />
                                <AuthenticatedRoute exact path="/admin/projects/:trackingCode" component={Project.Details} />

                                <Route exact path="*" component={NotFound} />
                            </Switch>
                        </div>
                    </div>
                </div>
            </Router>
        )
    }
}
export default ComponentWithStore(App)
