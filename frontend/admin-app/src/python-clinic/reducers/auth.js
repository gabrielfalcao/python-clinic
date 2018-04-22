const DEFAULT_STATE =  {
    token: null,
    error: null
}

export const auth = (state = DEFAULT_STATE, action = {}) => {
    const {type, ...payload} = action

    switch (type) {
        case 'AUTHENTICATION_ERROR':
            let {error, credentials} = payload
            return {...state, error: {...error, credentials: credentials}}

        case 'NEW_AUTHENTICATION':
            return {...state, token: payload, error:null}

        case 'LOGOUT':
            return {...DEFAULT_STATE}

        default:
            return {...state}
    }
}

export default auth
