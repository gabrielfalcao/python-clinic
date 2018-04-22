import { connect } from 'react-redux'
import { withRouter } from "react-router-dom"
/* import { withRouter } from "react-router-dom"
 * */



export const ComponentWithStore = (Component) => {
    return withRouter(connect(
        (state) => {
            return {...state}
        },
        (dispatch) => {
            return {}
        }
    )(Component))
}
