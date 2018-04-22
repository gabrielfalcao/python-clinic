import React from "react"
import PropTypes from 'prop-types'

import {NotificationManager} from 'react-notifications'
import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import faBan from '@fortawesome/fontawesome-free-solid/faBan'
import faEraser from '@fortawesome/fontawesome-free-solid/faEraser'
import faEdit from '@fortawesome/fontawesome-free-solid/faEdit'
import faShippingFast from '@fortawesome/fontawesome-free-solid/faShippingFast'
import faSync from '@fortawesome/fontawesome-free-solid/faSync'
import faTruckLoading from '@fortawesome/fontawesome-free-solid/faTruckLoading'

import {ComponentWithStore} from 'python-clinic/utils/ui'

import Item from './Item'
import VisibilityButton from './VisibilityButton'
import QueryInput from './QueryInput'


export class List extends React.Component {
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

    refresh = () => {
        const {context, props, api} = this
        const {store} = context
        const {auth} = props


        localStorage.removeItem('pythonclinic.state')
        store.dispatch({
            type: 'UNLOAD_PROJECTS',
        })

        api.loadProjectList(auth.token.tenant, auth.token.envchar, (projects)=>{
            if (!projects) {
                return
            }
            let title = (projects && projects.length !== 1) ? "projects" : "project"
            NotificationManager.success(`${projects.length} ${title} found.`, `Good News`)
        })
    }
    onTypeQuery = (event) => {
        const {store} = this.context
        const text = event.target.value;
        const shouldSubmit = event.charCode === 13
        if (shouldSubmit) {
            store.dispatch({
                type: 'FILTER_PROJECTS_BY_ALL_CRITERIA',
                query: text
            })
        }
    }
    hasItemsReady = () => {
        const {projects} = this.props
        return ((projects.loaded) || (projects.all && projects.all.length > 0))
    }
    onClickRefresh = (event) => {
        event.preventDefault()
        this.refresh()
    }
    onClickReset = (event) => {
        const {store} = this.context
        event.preventDefault()
        store.dispatch({
            type: 'RESET_PROJECT_FILTERS',
        })

    }
    isLoading = () => {
        const {projects} = this.props
        return (!projects.loaded)
    }
    showLoading = () => {
        const {isLoading, onClickRefresh} = this
        if (!isLoading()) {
            return null
        }
        return (
            <div className="pt-4">
                <center>loading projects...</center>
                <center>
                    <button className={`btn btn-sm btn-link text-success`} onClick={onClickRefresh}>
                        <FontAwesomeIcon icon={faSync} size="4x" pulse />
                    </button>
                </center>
                <br />
                <center><em className="text-secondary">click on the spinning icon above if this seems to get stuck :)</em></center>
            </div>
        )
    }
    removeKeyFromFilterCriteria = (key, value) => {
        const {store} = this.context
        store.dispatch({
            key, value,
            type: 'REMOVE_FROM_PROJECT_FILTER_CRITERIA',
        })
    }
    render() {
        const {onTypeQuery, onClickRefresh, onClickReset, hasItemsReady, removeKeyFromFilterCriteria} = this
        const {projects} = this.props
        let title = (projects.filtered && projects.filtered.length !== 1) ? "Projects" : "Project"

        let titleClass = "h2 text-primary"
        if (projects.filter) {
            title = `${projects.filtered ? projects.filtered.length: "No"} ${title} ${projects.filter.label ? projects.filter.label: ""}`
            titleClass = "h2 text-"+projects.filter.color
        } else if (projects.filtered) {
            title = `${projects.filtered.length} ${title}`
        }
        let filterPlaceholder = "try typing 'order' or 'tracking_code'"
        let currentFilters = [
            projects.filter && projects.filter.value ? `${projects.filter.key}: "${projects.filter.value}"` : null,
            projects.query || filterPlaceholder
        ]
        let filterDefaultValue = currentFilters.filter((o)=>(typeof o === "string")).join(' ')
        return (
            <div className="col-xl-10 col-lg-9 pt-5">
                {hasItemsReady() ? [
                     <div className="row pt-4" key="projects-toolbar">
                         <div className="col-lg-6 col-md-6 col-sm-12">
                             <span className={titleClass}>
                                 <button className={`btn btn-sm btn-outline-success pb-1`} onClick={onClickRefresh}>
                                     <FontAwesomeIcon icon={faSync} size="2x" />
                                 </button>
                                 &nbsp;
                                 <span>{title}</span>
                             </span>
                         </div>
                         <div className="col-lg-6 col-sm-12 btn-group">
                             <div className="container">
                                 <div className="row pt-2">
                                     <button className={`btn btn-sm btn-outline-secondary col`} onClick={onClickReset}>
                                         <FontAwesomeIcon icon={faEraser} size="2x" />
                                     </button>
                                     <VisibilityButton key="0" color="info" value="assigned" icon={faEdit} name="Assigned" />
                                     <VisibilityButton key="1" color="warning" value="in_transit" icon={faShippingFast} name="Out For Delivery" />
                                     <VisibilityButton key="2" color="danger" value="canceled" icon={faBan} name="Canceled" />
                                     <VisibilityButton key="3" color="success"  value="delivered" icon={faTruckLoading} name="Completed" />
                                 </div>
                             </div>
                         </div>
                     </div>,
                     <div className="row pt-2" key="projects-searchbar">
                         <div className="col-lg-12 col-md-12 col-sm-12">
                             <QueryInput onTypeQuery={onTypeQuery} placeholder={filterPlaceholder} defaultValue={filterDefaultValue} projects={projects.filtered} />
                         </div>
                     </div>,
                     <div className="row pt-2" key="projects-filter-criteria">
                         <div className="col-lg-12 col-md-12 col-sm-12">
                             {(projects.criteria && Object.keys(projects.criteria).length > 0) ? [<code>filters:&nbsp;</code>].concat(Object.entries(projects.criteria).map(([key, value], index) => {
                                  const handleClick = (e) => {
                                      e.preventDefault()
                                      removeKeyFromFilterCriteria(key, value)
                                  }
                                  return (
                                      <span className={`btn btn-sm btn-outline-secondary`} key={`criteria-filter-by-${key}`} onClick={handleClick}>
                                          <center>
                                              <span>{key}</span>
                                              <br />
                                              <strong>{value}</strong>
                                          </center>
                                      </span>
                                  )
                              })) : null}
                         </div>
                     </div>,
                 ]: null}
                {this.showLoading() || (
                    <div className="row pt-4">
                         <div className="col">
                             <table className="table">
                                 <thead>
                                     <tr>
                                         <th scope="col">details</th>
                                         <th className="d-none d-xl-block d-lg-block d-md-block d-xs-none d-sm-none" scope="col">
                                             <div className="row">
                                                 <div className="col-6">
                                                     From
                                                 </div>
                                                 <div className="col-6">
                                                     To
                                                 </div>
                                             </div>
                                         </th>
                                         <th scope="col">Tracking Url</th>
                                     </tr>
                                 </thead>
                                 <tbody>
                                     {projects.filtered ? projects.filtered.map((item, key) => <Item key={key} project={item} />): null}
                                 </tbody>
                             </table>
                         </div>
                     </div>
                 )}
            </div>
        )
    }
}

export default ComponentWithStore(List)
