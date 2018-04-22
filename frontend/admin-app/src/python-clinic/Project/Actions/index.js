import './Actions.css'

import React from "react"
import PropTypes from 'prop-types'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'

import faInfoCircle from '@fortawesome/fontawesome-free-solid/faInfoCircle'
import faBan from '@fortawesome/fontawesome-free-solid/faBan'
import faEnvelope from '@fortawesome/fontawesome-free-solid/faEnvelope'

import faShippingFast from '@fortawesome/fontawesome-free-solid/faShippingFast'
import faTruckLoading from '@fortawesome/fontawesome-free-solid/faTruckLoading'
import faClipboard from '@fortawesome/fontawesome-free-solid/faClipboard'
import faFilePdf from '@fortawesome/fontawesome-free-solid/faFilePdf'

import { Link, withRouter } from "react-router-dom"
import { NotificationManager } from 'react-notifications'
import {ComponentWithStore} from 'python-clinic/utils/ui'
import Clipboard from 'react-clipboard.js';
import {auth_is_active} from 'python-clinic/utils/auth'


export const Button = ComponentWithStore(({className, children, onClick, action}) => (
    <button action={action} onClick={onClick} className={`btn btn-sm ${className}`}>{children}</button>
))
export const ActionButton = ComponentWithStore(({map, project, action, showText}) => {
    const {pattern, label, icon, className='col', call} = map[action]
    const {status} = project
    if (!status || !status.match(pattern)) {
        return null
    }

    return (
        <Button action={action} onClick={() => { call(project); return true }} className={className}><FontAwesomeIcon icon={icon} /> {showText ? label: null}</Button>
    )
})
export class Actions extends React.Component {
    static contextTypes = {
        api: PropTypes.object,
        store: PropTypes.object,
    }
    static defaultProps = {
        project: {status:"", label_url: ""},
        showText: true,
        detailsLink: false,
    }
    static propTypes = {
        project: PropTypes.object,
        history: PropTypes.object,
        showText: PropTypes.bool,
        detailsLink: PropTypes.bool,
        auth: PropTypes.object.isRequired,
    }
    getAccessToken = () => {
        const {auth, history} = this.props

        if (auth_is_active(auth)) {
            return auth.token.access_token
        } else {
            NotificationManager.error('Please authenticate again', 'Token Expired!', 5000)
            setTimeout(() => {
                history.push('/admin/logout')
            }, 5000)
        }
    }

    get api () {
        return this.context.api
    }

    deliverProject = (project) => {
        this.api.deliverProject(project, (response)=>{
            response.ok && NotificationManager.success(`A truck just left with ${project.tracking_code}`, 'Project In-Transit!')
        })
        return true
    }
    confirmDelivered = (project) => {
        this.api.confirmDelivered(project, (response)=>{
            response.ok && NotificationManager.success(`A truck just left with ${project.tracking_code}`, 'Project In-Transit!')
        })
        return true
    }
    cancelProject = (project) => {
        this.api.cancelProject(project, (response)=>{
            response.ok && NotificationManager.warning(`The project ${project.tracking_code} has been canceled`, 'Project Canceled')
        })
        return true
    }
    notifyProjectStatus = (project) => {
        this.api.notifyProjectStatus(project)
        return true
    }
    onCopyToClipboard = () => {
        const {props} = this
        const {project} = props
        NotificationManager.warning(`Ready to paste the JSON anywhere!`, `${project.tracking_code} is in your clipboard`)
    }
    mapping = () => (
        {
            deliver: {
                call: this.deliverProject,
                className: "btn-outline-warning",
                icon: faShippingFast,
                label: "Send to Delivery",
                pattern: /assigned/
            },
            cancel: {
                call: this.cancelProject,
                className: "btn-outline-danger",
                icon: faBan,
                label:"Cancel Project",
                pattern: /assigned/
            },
            handout: {
                call: this.confirmDelivered,
                className: "btn-outline-success",
                icon: faTruckLoading,
                label:"Confirm Handout",
                pattern: /in_transit/
            },
            notify: {
                call: this.notifyProjectStatus,
                className: "btn-outline-primary",
                icon: faEnvelope,
                label:"Push Status",
                pattern: /in_transit|canceled|returned|delivered/,
            },
        }
    )
    render() {
        const {props, onCopyToClipboard} = this
        const {project, showText, detailsLink, history} = props
        const ctx = {
            map: this.mapping(),
            project: project,
            showText: showText
        }

        return ([
            (detailsLink ? <Link key={`${project.tracking_code}-item-info`} className="btn btn-sm btn-outline-secondary" to={`/admin/projects/${project.tracking_code}`}><FontAwesomeIcon icon={faInfoCircle} /> {showText ? "View": null}</Link>: null),
            <ActionButton key={`${project.tracking_code}-do-deliver`} action="deliver" {...ctx}  />,
            <ActionButton key={`${project.tracking_code}-do-cancel`} action="cancel" {...ctx}  />,
            <ActionButton key={`${project.tracking_code}-do-handout`} action="handout" {...ctx}  />,
            <ActionButton key={`${project.tracking_code}-no-notify`} action="notify" {...ctx}  />,
            <a key={`${project.tracking_code}-item-pdf`} className="btn btn-sm btn-outline-info" href={project.label_url} target="_new">
                <FontAwesomeIcon icon={faFilePdf} /> {showText ? "PDF": null}
            </a>,
            <Clipboard key={`${project.tracking_code}-do-copy-json`} onSuccess={onCopyToClipboard} component="a" className="btn btn-sm btn-outline-primary" button-href={history.location.pathname} data-clipboard-text={JSON.stringify(project, null, 4)}>
                <div><FontAwesomeIcon icon={faClipboard} /> {showText ? "Copy JSON": null}</div>
            </Clipboard>,
        ])
    }
}

export default ComponentWithStore(withRouter(Actions))
