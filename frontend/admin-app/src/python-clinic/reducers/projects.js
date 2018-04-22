import filter_by from 'python-clinic/utils/filter_by'
import {string_to_criteria} from 'python-clinic/utils/query_language'
import {criteria_to_string} from 'python-clinic/utils/query_language'

const INITIAL_EMPTY_STATE = {
    all: [],
    filtered:[],
    loaded: false,
    criteria: null,
    query: null
}
const criteria_from_raw_text = (text) => {
    if ((!text) || text.length === 0) {
        return null
    }
    let criteria = string_to_criteria(text)

    if (Object.keys(criteria).length > 0) {
        return criteria
    }
    return {
        "request_data.external_order_id": text,
        "order": text,
        "tracking_code": text,
        "return_tracking_code": text,
    }
}

const apply_filter_criteria = (items, {...criteria}) => {
    if (Object.keys(criteria).length < 1) {
        // return all items if criteria is empty
        return [...items]
    }
    return filter_by.all(items, criteria)
}

export const projects = (state = INITIAL_EMPTY_STATE, action = {}) => {
    let all_criteria
    let merged_criteria
    let new_criteria
    let filtered
    switch (action.type) {
        case 'REMOVE_FROM_PROJECT_FILTER_CRITERIA':
            if (!state.criteria) {
                return {...state}
            }
            new_criteria = {...state.criteria}
            delete new_criteria[action.key]

            filtered = apply_filter_criteria(state.all, new_criteria)
            return {...state, criteria: new_criteria, filtered: filtered, all: state.all}

        case 'FILTER_PROJECTS_BY_ALL_CRITERIA':
            all_criteria = criteria_from_raw_text(action.query)
            if (!all_criteria) {
                return {...state, criteria: null, query: null}
            }
            merged_criteria = {...state.criteria, ...all_criteria}
            filtered = apply_filter_criteria(state.all, merged_criteria)
            return {
                ...state,
                filtered: filtered,
                criteria: merged_criteria,
                query: criteria_to_string(merged_criteria),
            }

        case 'LOGOUT':
        case 'UNLOAD_PROJECTS':
            return {...INITIAL_EMPTY_STATE}

        case 'RESET_PROJECT_FILTERS':
            return {...state, filtered: state.all, criteria: null, query: null}

        case 'SET_PROJECTS':
            filtered = action.projects
            if (state.criteria) {
                filtered = apply_filter_criteria(action.projects || [], state.criteria)
            }
            return {...state, filtered: filtered, all: action.projects || [], loaded: true, error: action.error || null}

        case 'LOADING_PROJECTS':
            return {...state, loaded: false, current: null}

        case 'CHANGE_PROJECT':
            return {...state, current: action.project, error: action.error, loaded: true}

        default:
            return {...state}
    }
}

export default projects
