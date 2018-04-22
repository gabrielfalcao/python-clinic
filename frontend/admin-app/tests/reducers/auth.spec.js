import React from 'react'
import configureStore from 'redux-mock-store'

import {auth} from 'python-clinic/reducers/auth'
import {now} from 'python-clinic/utils/datetime'


describe('reducers.auth', ()=>{
    const mockStore = configureStore()
    let initialState = {}
    let action
    let store

    const reduce = ({...action}) => auth(undefined, action)

    beforeEach(()=>{
        store = mockStore(initialState)
    })

    it('should authenticate a user', () => {
        // Given an empty store
        store = mockStore({ })
        action = {
            type: 'NEW_AUTHENTICATION',
            access_token: 'must-be-important',
            refresh_token: 'refresh-with-me',
            expires_in: 86400,
            username: 'ignored-attribute',
            scope: 'every:thing for:sure',
            authenticated_at: 102030405060,
            expires_at: 8070605040,
            username: 'johndoe',
            password: 'insecure',
            tenant: 'dodici',
            envchar: 'x'
        }
        let {error, token} = reduce(action)

        expect(error).to.be.null
        expect(token).to.be.an('object')

        expect(token).to.have.property("access_token", "must-be-important")
        expect(token).to.have.property("expires_in", 86400)
        expect(token).to.have.property("refresh_token", "refresh-with-me")
        expect(token).to.have.property("scope", "every:thing for:sure")
        expect(token).to.have.property("authenticated_at")
        expect(token.authenticated_at).to.be.a('number')

        expect(token).to.have.property("expires_at")
        expect(token.expires_at).to.be.a('number')

        expect(token).to.have.property("username", "johndoe")
        expect(token).to.have.property("password", "insecure")
    })

    it('should logout', () => {
        // Given an empty store
        store = mockStore({
            auth: {
                token: {
                    "access_token": "must-be-important",
                    "refresh_token": "refresh-with-me",
                    "username": "johndoe",
                    "expires_in": 86400,
                    "pass": "insecure",
                    "scope": "every:thing for:sure",
                    "authenticated_at": now() - 86400,
                    "expires_at": now()
                }
            }
        })

        action = {
            type: 'LOGOUT',
        }
        let auth = reduce(action)
        expect(auth).to.deep.equal({
            token: null,
            error: null,
        })
    })
})
