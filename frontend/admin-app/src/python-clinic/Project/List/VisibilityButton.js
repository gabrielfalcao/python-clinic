import React from "react"
import PropTypes from 'prop-types'

import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import {ComponentWithStore} from 'python-clinic/utils/ui'

export class VisibilityButton extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }

    static propTypes = {
        value: PropTypes.string,
        icon: PropTypes.object,
        projects: PropTypes.object.isRequired,
    }
    handleClick = (e) => {
        const {store} = this.context
        const {value} = this.props
        e.preventDefault()

        store.dispatch({
            type: 'FILTER_PROJECTS_BY_ALL_CRITERIA',
            query: `status: "${value}"`,
        })

    }
    render() {
        const {props, handleClick} = this
        const {name=null, value, color, icon=null} = props
        return (
            <button key={`v-btn-${value}`} className={`btn text-sm col mr-2 btn-sm btn-outline-${color}`} onClick={handleClick}>
                {icon ? <FontAwesomeIcon icon={icon} size="2x" />: name}
            </button>
        )
    }
}
export default ComponentWithStore(VisibilityButton)
