import React from "react"
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { Link } from "react-router-dom"

import Actions from 'python-clinic/Project/Actions'

class Item extends React.Component {
    static propTypes = {
        project: PropTypes.object.isRequired,
    }

    render() {
        const {project} = this.props
        return ([
            <tr key={`${project.slug}-details`}>
                <td>
                    <Link to={`/admin/projects/${project.slug}`}>{project.name}</Link>
                </td>
            </tr>,
        ])
    }
}

const mapStateToProps = state => {
    return {...state}
}

const mapDispatchToProps = dispatch => {
    return {
    }
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(Item)
