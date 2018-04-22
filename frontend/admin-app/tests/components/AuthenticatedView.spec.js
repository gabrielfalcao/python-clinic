import React from 'react'

import { mount} from 'enzyme'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { Redirect } from 'react-router-dom'


import configureStore from 'redux-mock-store'

import { now } from 'python-clinic/utils/datetime'
import AuthenticatedView from 'python-clinic/components/AuthenticatedView'

describe('AuthenticatedView', ()=>{
    const authenticatedState = {
        auth: {
            token: {
                expires_at: (now() + 1000),
                access_token: 'secure',
            }
        }
    }
    const mockStore = configureStore()
    let store
    let view

    describe('when authenticated', () => {
        beforeEach(()=>{
            store = mockStore(authenticatedState)
        })

        it('should render its children when auth.token.expires_at is greater than the current unix timestamp', () => {

            const auth = {
                token: {
                    expires_at: (now() + 3000),
                    access_token: 'secure',
                }
            }
            view = mount((
                <MemoryRouter>
                    <Provider store={store}>
                        <AuthenticatedView auth={auth}>
                            <p>successfully authenticated</p>
                        </AuthenticatedView>
                    </Provider>
                </MemoryRouter>
            ))

            expect(view.find("p").text()).to.equal('successfully authenticated')
        })
    })
    describe('when *not* authenticated', () => {
        beforeEach(()=>{
            // Given an empty redux store
            store = mockStore({})
        })

        it('should render a redirect to the login page when not authenticated', () => {
            view = mount((
                <MemoryRouter>
                    <Provider store={store}>
                        <AuthenticatedView  auth={{token: null}}>
                            <p>successfully authenticated</p>
                        </AuthenticatedView>
                    </Provider>
                </MemoryRouter>
            ))

            expect(view.find("p").length).to.equal(0)
            expect(view.find(Redirect).length).to.equal(1)
            expect(view.find(Redirect).prop('to')).to.equal("/admin/login")
        })

        it('should render nothing if not authenticated and the prop noRedirect is set', () => {
            view = mount((
                <MemoryRouter>
                    <Provider store={store}>
                        <AuthenticatedView auth={{token: null}} noRedirect>
                            <p>successfully authenticated</p>
                        </AuthenticatedView>
                    </Provider>
                </MemoryRouter>
            ))

            expect(view.find(Redirect).length).to.equal(0)
            expect(view.find("p").length).to.equal(0)
        })
    })
})
