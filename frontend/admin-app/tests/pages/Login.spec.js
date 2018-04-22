import React from 'react'

import { mount} from 'enzyme'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { Redirect } from 'react-router-dom'
import {now} from 'python-clinic/utils/datetime'

import configureStore from 'redux-mock-store'

import Login from 'python-clinic/pages/Login'


describe('Login', ()=>{
    const initialState = {
        auth: {
            token: {
                expires_at: (now() + 1000)
            }
        }
    }

    const initialProps = {}
    const mockStore = configureStore()
    let store
    let view

    beforeEach(()=>{
        store = mockStore(initialState)
    })

    it('should redirect to /admin/projects when props.auth.token.expires_at is greated than the current unix timestamp', () => {

        const auth = {
            token: {
                expires_at: (now() + 1000)
            }
        }
        view = mount((
            <MemoryRouter initialEntries={[ '/random' ]}>
                <Provider store={store}>
                    <Login auth={auth}>
                        <p>worked</p>
                    </Login>
                </Provider>
            </MemoryRouter>
        ))

        expect(view.find(Redirect).length).to.equal(1)
        expect(view.find(Redirect).first().prop('to')).to.equal('/admin/projects')
    })
})
