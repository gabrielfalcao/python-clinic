const DEFAULT_STATE = {
    config: {},
}

export const internal = (state = DEFAULT_STATE, action={}) => {
    switch (action.type) {
        case 'SET_INTERNAL_CONFIG':
            return {config: action.config}
        default:
            return {...state}
    }
}

export default internal
