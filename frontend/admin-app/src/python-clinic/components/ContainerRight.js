import React from "react"
import PropTypes from 'prop-types'

import {ComponentWithStore} from 'python-clinic/utils/ui'


const ContainerRight = ({ children, className="container-fluid"}) => (
    <div className={`python-clinic-inner-container ${className}`}>
        <div className="row">
            <div className="col-12">
                {children}
            </div>
        </div>
    </div>
)

ContainerRight.contextTypes = {
    store: PropTypes.object,
    router: PropTypes.object,
}

export default ComponentWithStore(ContainerRight)
