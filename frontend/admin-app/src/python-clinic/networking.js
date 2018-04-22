import request from 'superagent'
import {config} from './conf'
import {NotificationManager} from 'react-notifications'


const BASE_URL = config.base_url()

function forward(response, then, error) {
    const errorMessage = (""+error+"")
    if (error && !response) {
        response = {ok: false, ...error, body: {}}
        error.response = response
    } else if (error) {
        error.response = response
    }

    if (errorMessage.match(/network.* offline/)) {
        NotificationManager.error(errorMessage, 'Network Error')
        return then(response, error)
    }

    if (!response.ok) {
        if (response.body.message) {
            let title
            switch (response.status) {
                case 400:
                    title = 'invalid request'
                    break
                case 409:
                    title = 'conclict'
                    break;
                case 500:
                    title = 'server error'
                    break
                default:
                    title = `Http Error ${response.status}`
            }
            let message = response.body.message

            if (response.body.data) {
                alert('data in response')
                console.log(response.body)
                message = response.body.data.message
            }
            NotificationManager.error(message, title)
        } else {
            NotificationManager.error(errorMessage, 'HTTP Request')
        }
    }

    return then(response, error)
}

export class PythonClinicHttpClient {
    constructor(baseUrl=BASE_URL, token=null){
        this.baseUrl = baseUrl
        this.token = token
    }
    isTokenAvailable = () => {
        return this.token || false
    }
    ensureTokenIsAvailable = () => {
        if (this.isTokenAvailable()) {
            return true
        }
        const msg = `Token is ${this.token}`
        NotificationManager.error(msg, 'Invalid Access Token')
    }


    getProjectByTrackingCode = (trackingCode, then) => {
        request
            .get(`${BASE_URL}/api/v1/project/${trackingCode}`)
            .set('Accept', 'application/json')
            .set('Content-Type', 'application/json')
            .end((error, response) => forward(response, then, error))
    }
    retrieveProjectsList = (tenant=null, envchar=null, then) =>{
        let url
        if (tenant && envchar) {
            url = `${BASE_URL}/api/v1/projects/${tenant}/${envchar}`
        } else {
            url = `${BASE_URL}/api/v1/projects`
        }
        request.get(url)
               .set('Accept', 'application/json')
               .set('Content-Type', 'application/json')
               .end((error, response) => forward(response, then, error))
    }
    cancelProject = (project, then) =>{
        if (!this.ensureTokenIsAvailable()) {return}
        const {tracking_code, request_data} = project
        const {tenant, envchar} = request_data
        request
            .post(`${BASE_URL}/python-clinic/traditional/adapter/v1/${tenant}/${envchar}/projects/${tracking_code}/_cancel`)
            .set('Accept', 'application/json')
            .set('Authorization', `Bearer ${this.token}`)
            .set('Content-Type', 'application/json')
            .end((error, response) => forward(response, then, error))
    }
    deliverProject = (project, then) => {
        if (!this.ensureTokenIsAvailable()) {return}

        const {tracking_code} = project
        request
            .post(`${BASE_URL}/api/v1/project/${tracking_code}/deliver`)
            .set('Accept', 'application/json')
            .set('Authorization', `Bearer ${this.token}`)
            .set('Content-Type', 'application/json')
            .end((error, response) => forward(response, then, error))
    }
    confirmDelivered = (project, then) => {
        if (!this.ensureTokenIsAvailable()) {return}

        const {tracking_code} = project
        request
            .post(`${BASE_URL}/api/v1/project/${tracking_code}/confirm_delivered`)
            .set('Accept', 'application/json')
            .set('Content-Type', 'application/json')
            .set('Authorization', `Bearer ${this.token}`)
            .end((error, response) => forward(response, then, error))
    }
    notifyProjectStatus = (project, reason, then) => {
        if (!this.ensureTokenIsAvailable()) {return}

        const {tracking_code, request_data} = project
        const {tenant, envchar} = request_data
        request
            .post(`${BASE_URL}/api/v1/${tenant}/${envchar}/project/${tracking_code}/status`)
            .send({ status: project.status, reason: reason })
            .set('Accept', 'application/json')
            .set('Content-Type', 'application/json')
            .set('Authorization', `Bearer ${this.token}`)
            .end((error, response) => forward(response, then, error))
    }
    tenantLogin = (tenant, envchar, username, password, then) => {
        request
            .post(`${BASE_URL}/api/v1/${tenant}/${envchar}/login`)
            .send({username: username, password: password})
            .set('Accept', 'application/json')
            .set('Content-Type', 'application/json')
            .end((error, response) => forward(response, then, error))
    }
}

export class PythonClinicReduxHttpClient {
    constructor(store, token=null) {
        this.store = store
        this.token = token
    }
    get api() {
        if (!this.token) {
            const state = this.store.getState()
            const {auth} = state
            const {token} = auth || {token: null}
            const {access_token} = token || {access_token: null}
            this.token = access_token
        }
        return new PythonClinicHttpClient(config.base_url(), this.token)
    }
    loadProjectList = (tenant=null, envchar=null, done=() => null) => {
        const {api, store} = this

        // backup state
        const {projects} = store.getState()

        api.retrieveProjectsList(tenant, envchar, (response, error) =>{
            const fresh_projects = response.body
            if (response.ok) {
                store.dispatch({
                    type: 'SET_PROJECTS',
                    projects: fresh_projects,
                })
                done(fresh_projects, null)
                if (fresh_projects.length === 0) {
                    /* NotificationManager.warning('Server found no projects', 'Empty Result')*/
                } else {
                    /* NotificationManager.info(`${projects.length} total`, 'Found ProjectList')*/
                }
            } else {
                const error_message = `failed to retrieve projects: ${error}`
                store.dispatch({
                    type: 'SET_PROJECTS',
                    projects: projects,
                    error: error_message
                })
                NotificationManager.error('The project data available could not be updated', error_message)
                done(null, error_message)
            }

        })
    }
    loadProjectByTrackingCode = (trackingCode, done=() => null) => {
        const {api, store} = this
        api.getProjectByTrackingCode(trackingCode, (response, error) => {
            if (response.ok) {
                store.dispatch({
                    type: 'CHANGE_PROJECT',
                    project: response.body,
                    error: error
                })
            } else {
                store.dispatch({
                    type: 'CHANGE_PROJECT',
                    project: null,
                    error: `failed to retrieve project ${trackingCode}: ${error}`,
                })
            }
            done(response, error)
        })
    }
    cancelProject = (project, done=() => null) => {
        const {api, store, notifyProjectStatus, loadProjectList} = this
        api.cancelProject(project, (response, error) => {
            if (response.ok) {
                store.dispatch({
                    type: 'CHANGE_PROJECT',
                    project: response.body,
                })
                notifyProjectStatus(response.body, 'Deleted by User')
            }
            loadProjectList()
            done(response, error)
        })
    }
    deliverProject = (project, done=() => null) => {
        const {api, store, notifyProjectStatus, loadProjectList} = this
        api.deliverProject(project, (response, error) => {
            if (response.ok) {
                store.dispatch({
                    type: 'CHANGE_PROJECT',
                    project: response.body,
                })
                notifyProjectStatus(response.body, 'Package left facility, out for delivery')
            }
            loadProjectList()
            done(response, error)
        })
    }
    confirmDelivered = (project, done=() => null) => {
        const {api, store, notifyProjectStatus, loadProjectList} = this
        api.confirmDelivered(project, (response, error) => {
            if (response.ok) {
                store.dispatch({
                    type: 'CHANGE_PROJECT',
                    project: response.body,
                })
                notifyProjectStatus(response.body, 'Package was delivered to final destination')
                loadProjectList()
            }

            done(response, error)
        })
    }
    notifyProjectStatus = (project, reason='Notify tenant api', done=() => null) => {
        const {api} = this
        NotificationManager.info(`Notifying tenant of status change ${project.status}`, `${project.tracking_code}`, 5000)

        api.notifyProjectStatus(project, reason, (response, error) => {
            done(response.body, error)
        })
    }
    tenantLogin = (tenant, envchar, username, password, done=() => null) => {
        const {api, store} = this
        api.tenantLogin(tenant, envchar, username, password, (response, error) => {
            if (response.ok) {
                const result = {
                    ...response.body,
                    tenant: tenant,
                    envchar: envchar,
                    username: username,
                    password: password,
                }
                let envname
                switch(envchar) {
                    case "x":
                        envname = "sandbox";
                        break;
                    case "v":
                        envname = "development";
                        break;
                    case "p":
                        envname = "production";
                        break;
                    case "s":
                        envname = "stage";
                        break;
                    default:
                        break;
                }
                result['envname'] = envname

                const action = {
                    ...result,
                    type: 'NEW_AUTHENTICATION',
                }
                store.dispatch(action)
                localStorage.setItem(`pythonclinic.auth`, JSON.stringify(action))
                done(result, null)

            } else {
                store.dispatch({
                    type: 'AUTHENTICATION_ERROR',
                    error: response.body,
                    credentials: {
                        tenant: tenant,
                        envchar: envchar,
                        username: username,
                    }
                })
            }
        })
    }
}

export default PythonClinicReduxHttpClient
