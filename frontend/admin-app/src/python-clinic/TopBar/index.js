import React from "react"
import PropTypes from 'prop-types'

import CountDownClock from './CountDownClock';
import { auth_is_active } from 'python-clinic/utils/auth'
import { ComponentWithStore } from 'python-clinic/utils/ui'

import * as Feather from 'react-feather'
import TITLE from 'python-clinic/constants'


class TopBar extends React.Component {
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
        if (!auth_is_active(auth)) {
            return null
        }
        return (
            <div>
                <nav className="navbar navbar-dark fixed-top bg-dark flex-md-nowrap collapse navbar-collapse show" style={{marginBottom: '50px'}}>
                    <a className="text-warning brand" href="/admin/projects">
                        <Feather.Package size="24px" style={{margin: 0, padding: 0, display: 'inline', float: 'left'}} /> &nbsp; {TITLE}.
                    </a>

                    <div>
            <span className="badge badge-pill badge-warning">
                            {auth.token.username}&nbsp;<br />
                            {auth.token.tenant}&nbsp;<br />
                            {auth.token.envname}
                        </span>
                        <span className="badge badge-pill  badge-info">
                            &nbsp;<br />
                            <CountDownClock timeout={auth.token.expires_at} />
                            <br />&nbsp;
                        </span>
                    </div>

                </nav>
            </div>
        )
    }
}
export default ComponentWithStore(TopBar)
