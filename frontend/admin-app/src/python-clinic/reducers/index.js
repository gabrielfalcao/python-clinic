import { combineReducers } from 'redux'
import { compose } from 'redux'
import { auth } from 'python-clinic/reducers/auth'
import { projects } from 'python-clinic/reducers/projects'
import { internal } from 'python-clinic/reducers/internal'

const DEFAULT_STATE = {}

export const mainReducer = (state = DEFAULT_STATE, action = {}) => {
    switch (action.type) {
        default:
            return {...state}
    }
}

export default compose(mainReducer, combineReducers({ auth, projects, internal }))
