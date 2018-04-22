import $ from 'jquery'
import React from "react"
import PropTypes from 'prop-types'
import { Redirect } from "react-router-dom"
import { withRouter } from "react-router-dom"
import Inspector from 'react-inspector';

import Spinner from 'python-clinic/components/Spinner'
import ContainerRight from 'python-clinic/components/ContainerRight'

import {NotificationManager} from 'react-notifications'

import {ComponentWithStore} from 'python-clinic/utils/ui'
import {auth_is_active} from 'python-clinic/utils/auth'
import * as Feather from 'react-feather'
import TITLE from 'python-clinic/constants'


export const Field = ({name, type='text', label=null, defaultValue=null, placeholder=null, onChange}) => (
    <div className="container" field={name}>
        <div className="row">
            <div className="col-4">
                <p className={`form-label ${name} text-dark`} label={name}>{label.toUpperCase()}</p>
            </div>
            <div className="col-8">
                <input type={type} name={name} className={`form-control form-control-sm ${name}`} value={defaultValue ? defaultValue: ""} onChange={onChange} placeholder={placeholder} />
            </div>
        </div>
    </div>
)

export const ComboBox = ({name, label=null, defaultValue=null, choices={}, onChange}) => (
    <div className="container" field={name}>
        <div className="row">
            <div className="col-4">
                <p className={`form-label ${name} text-dark `}>{label.toUpperCase()}</p>
            </div>
            <div className="col-8">
                <select className={`form-control form-control-sm ${name}`} onChange={onChange} defaultValue={defaultValue}>
                    {Object.keys(choices).map((label, index) => {
                         const value = choices[label]
                         return <option key={index} value={value}>{label}</option>
                     })}
                </select>
            </div>
        </div>
    </div>
)

export const AuthError = ({error}) => (
    <div className="alert alert-danger" style={{textAlign: 'left'}}>
        <h4 className="alert-heading">Error</h4>
        <Inspector data={error} expandLevel={3} name={error.message} />
    </div>
)

export class Login extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
        api: PropTypes.object,
    }
    static defaultProps = {
        auth: {
            tenant: 'dodici',
            envchar: 'x'
        },
    }
    static propTypes = {
        auth: PropTypes.object,
        location: PropTypes.object,
    }
    state = {
        tenant: 'dodici',
        envchar: 'x',
        loading: false,
    }
    getFormValues = () => {
        const keys = [
            'username',
            'password',
            'tenant',
            'envchar',
        ]
        const values = {}

        keys.forEach((key, index) => {
            const fromStorage = localStorage.getItem(`pythonclinic.${key}`)
            const fromState = this.state[key]
            const fromProps = this.props.auth[key]
            const value = fromProps || fromStorage || fromState

            values[key] = value
        })

        return values
    }
    get api () {
        return this.context.api
    }

    formLogin = (e) => {
        e.preventDefault()
        this.setState({loading: true})
        const {username, password, tenant, envchar} = this.getFormValues()

        this.api.tenantLogin(tenant, envchar, username, password, (data) => {

            NotificationManager.success(`Hello ${data.username}`, `Welcome to ${data.tenant} ${data.envname}`, 5000)

            this.api.loadProjectList(tenant, envchar)
        })
    }
    captureField = (name) => {
        const data = {}
        data[name] = null

        return ({target, ...args}) => {
            const value = $(target).val()
            data[name] = value
            this.setState(data)
            localStorage.setItem(`pythonclinic.${name}`, value)
            return true
        }
    }
    componentWillMount() {
        const {store} = this.context
        const actionData = localStorage.getItem('pythonclinic.auth')
        const authAction = JSON.parse(actionData)
        if (authAction) {
            store.dispatch(authAction)
        }
    }
    render() {
        const {formLogin, props, captureField} = this
        const {loading} = this.state
        const {username, password, tenant, envchar} = this.getFormValues()
        const {auth} = props
        if (auth_is_active(auth)) {
            return <Redirect to={'/admin/projects'} />;
        }
        return (
            <ContainerRight className="container-fluid col-lg-12">
                <div className="login-page">
                    {loading ? <Spinner size="6x" /> : (
                         <form className="form-signin col-md-6 col-sm-12">
                             <br />
                             <Feather.Package size="128px" />
                             <br />
                             <br />
                             <h3 className="mb-3">{TITLE}</h3>
                             {auth.error ? <AuthError error={auth.error} /> : null}
                             <Field name="tenant" label="tenant" defaultValue={tenant} onChange={captureField('tenant')} />
                             <ComboBox name="envchar" label="Environment" defaultValue={envchar} onChange={captureField('envchar')} choices={{
                                 'dev': 'v',
                                 'sandbox': 'x',
                                 'staging': 's',
                                 'prod': 'p',
                             }}/>
                             <Field name="username" label="auth0 email" placeholder="username@python.clinic" defaultValue={username} type="email" onChange={captureField('username')}/>
                             <Field name="password" label="auth0 password" placeholder="auth0 password" defaultValue={password} type="password" onChange={captureField('password')} />
                             <button className="btn btn-outline-warning btn-primary btn-block" onClick={formLogin}>Sign in</button>
                         </form>)}
                </div>
            </ContainerRight>
        )
    }
}

export default ComponentWithStore(withRouter(Login))
