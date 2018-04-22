import React from "react"
import PropTypes from 'prop-types'

import Actions from 'python-clinic/Project/Actions'
/* import Clipboard from 'react-clipboard.js';*/

import { NotificationManager } from 'react-notifications'
import { history } from 'python-clinic/utils/history'
import { ComponentWithStore } from 'python-clinic/utils/ui'

import Spinner from 'python-clinic/components/Spinner'


export class ProjectDetails extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
        api: PropTypes.object,
    }
    static defaultProps = {
        projects: {list: [], all: []},
        auth: {token: null},
    }
    static propTypes = {
        projects: PropTypes.object,
        auth: PropTypes.object.isRequired,
    }
    get api () {
        return this.context.api
    }
    state = {
        loading: false,
        error: null
    }
    loadProject = (trackingCode) => {
        this.api.loadProjectByTrackingCode(trackingCode, (response, error) => {
            if (!response.ok || !response.body) {
                history.push('/projects')
            }
        })
    }
    deliverProject = (project) => {
        this.api.deliverProject(project, ()=>{
            /* history.push('/projects')*/
        })
    }
    cancelProject = (project) => {
        const {store} = this.context

        this.api.cancelProject(project, ()=>{
            NotificationManager.warning(`The project ${project.tracking_code} has been canceled`, 'Project Canceled')
            store.dispatch({
                type: 'CHANGE_PROJECT',
                project: project,
            })
        })
    }
    notifyProjectStatus = (project) => {
        this.api.notifyProjectStatus(project, ()=>{
            NotificationManager.success(`the Tenant API has been notified about the status ${project.status} of ${project.tracking_code}`, 'Push Succeeded!')
        })
    }

    componentWillMount() {
        const {match, projects} = this.props
        /* const {store} = this.context;*/
        const {trackingCode} = match.params

        if (!projects.current || projects.current.tracking_code !== trackingCode) {
            this.setState({loading: true})
            this.loadProject(trackingCode, (data, error)=>{
                this.setState({loading: false, error: error})
                if (error) {
                    history.push('/admin/projects')
                }
            })
        }
    }
    render() {
        const {props, state} = this
        const {projects} = props
        const {loading} = state
        const {current} = projects
        let request_data = (current ? current.request_data: {})

        return (
            <div>{current.name}</div>
        )
    }
}
export default ComponentWithStore(ProjectDetails)
