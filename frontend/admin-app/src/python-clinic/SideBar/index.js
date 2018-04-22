import React from "react"
import PropTypes from 'prop-types'

import MenuItem from './MenuItem'
import {auth_is_active} from 'python-clinic/utils/auth'
import {ComponentWithStore} from 'python-clinic/utils/ui'
import swaggerIcon from 'python-clinic/swagger.svg'

import * as Feather from 'react-feather'

const SideBarTitle = ({ name, className=""}) => {
    return (
        <h6 className={"sidebar-heading d-flex justify-content-between align-items-center mt-3 mb-3 " + className}>
            <span>{name}</span>
        </h6>
    )
}

class SideBar extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static defaultProps = {
        auth: {token: null},
    }
    static propTypes = {
        auth: PropTypes.object,
    }
    render() {
        const {auth} = this.props
        return (auth_is_active(auth) ? (
            <nav className="d-none col-xl-2 col-lg-2 col-md-2 bg-light d-lg-block d-xl-block d-xs-none d-sm-none d-md-none" style={{borderRight: '1px solid #ddd'}}>
                <div className="sidebar-sticky">
                    <ul className="nav flex-column pt-5">
                        <SideBarTitle name="Manage" className="text-dark" />
                        <ul className="nav flex-column mb-2">
                            <MenuItem name="Projects" to="/admin/projects" icon={Feather.Truck} />
                        </ul>
                        <SideBarTitle name="Session" className="text-dark" />
                        <ul className="nav flex-column mb-2">
                            <MenuItem name="Settings" to="/admin/settings" icon={Feather.Settings} />
                        </ul>
                        <ul className="nav flex-column mb-2">
                            <MenuItem name="Logout" to="/admin/logout" icon={Feather.LogOut} />
                        </ul>
                        <SideBarTitle name="API" className="text-dark" />
                        <ul className="nav flex-column mb-2">
                            <MenuItem name="Documentation" to="/docs/index.html" icon={Feather.Book} target="_self"/>
                            <MenuItem name="Explore with Swagger" to="/api" iconSrc={swaggerIcon} target="_self"/>
                        </ul>
                    </ul>

                </div>
            </nav>
        ) : null)
    }
}

export default ComponentWithStore(SideBar)
