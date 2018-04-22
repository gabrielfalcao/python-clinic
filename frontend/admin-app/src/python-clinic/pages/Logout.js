import React from "react"
import PropTypes from 'prop-types'

import {ComponentWithStore} from 'python-clinic/utils/ui'
import ContainerRight from 'python-clinic/components/ContainerRight'
import Spinner from 'python-clinic/components/Spinner'
import * as Feather from 'react-feather'


export class Logout extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static propTypes = {
        auth: PropTypes.object,
        history: PropTypes.object,
    }
    componentWillMount() {
        const {store} = this.context
        const {history} = this.props
        localStorage.removeItem('pythonclinic.auth')
        localStorage.removeItem('pythonclinic.state')
        store.dispatch({
            type: 'LOGOUT'
        })
        setTimeout(() => {
            history.push('/')
        }, 1047)
    }

    render() {
        return (
            <ContainerRight className="container-fluid col-lg-12">
                <div className="login-page">
                    <form className="form-signin col-md-6 col-sm-12">
                        <h1 className="mb-3">Bye bye</h1>
                        <br />
                        <Feather.Package size="256px" />
                        <br />
                        <br />
                        <Spinner />
                        <br />
                        <h3 className="mb-3">You are being redirected</h3>
                    </form>
                </div>
            </ContainerRight>
        )
    }
}

export default ComponentWithStore(Logout)
