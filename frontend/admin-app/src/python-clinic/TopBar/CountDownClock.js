import React from "react"
import PropTypes from 'prop-types'
import { Redirect } from "react-router-dom"
import { NotificationManager } from 'react-notifications'

import Countdown from 'react-countdown-now';


export class CountDownClock extends React.Component {
    static contextTypes = {
        store: PropTypes.object,
    }
    static propTypes = {
        timeout: PropTypes.number.isRequired,
        className: PropTypes.string,
    }
    renderer = ({ hours, minutes, seconds, completed }) => {
        const {props} = this
        const {className} = props
        if (completed) {
            NotificationManager.danger('You are being sent to the login page', 'Authentication Expired', 7000)
            return <Redirect to='/logout' />
        } else {
            // Render a countdown
            return <span className={`${className}`}>{hours}:{minutes}:{seconds}</span>;
        }
    };
    render() {
        const {renderer, props} = this
        const {timeout} = props
        return <Countdown date={timeout * 1000} renderer={renderer} />
    }
}

export default CountDownClock
