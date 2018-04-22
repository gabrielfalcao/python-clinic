import React from "react"

import FontAwesomeIcon from '@fortawesome/react-fontawesome'
import faSpinner from '@fortawesome/fontawesome-free-solid/faSpinner'


/**
 * Renders a FontawesomeIcon spinner with the given size
 * @constructor
 * @param {string} size - defaults to 3x
 */
const Spinner = ({size='3x'}) => (
    <center><FontAwesomeIcon spin size={size} icon={faSpinner} /></center>
)

export default Spinner
