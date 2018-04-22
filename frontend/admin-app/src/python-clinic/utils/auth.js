import {now} from 'python-clinic/utils/datetime'

export const token_has_expired = ({...token}) => {
    const current = now()
    return token.expires_at < current
}
export const auth_is_active = ({...auth}) => {
    return auth && auth.token && (!token_has_expired(auth.token))
}
