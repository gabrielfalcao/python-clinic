import React from "react"
import PropTypes from 'prop-types'
import * as Feather from 'react-feather'

import TITLE from 'python-clinic/constants'

import {ComponentWithStore} from 'python-clinic/utils/ui'


export class Welcome extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static propTypes = {
        location: PropTypes.object,
    }
    render() {
        return (
            <section className="section">
                <div className="container">
                    <h1 className="title">
                        {TITLE}
                    </h1>
                    <center>
                        <Feather.Code size="64px"/>
                    </center>
                    <p className="subtitle">
                        My first website with <strong>Bulma</strong>!
                    </p>
                </div>
            </section>
        )
    }
}

export default ComponentWithStore(Welcome)
