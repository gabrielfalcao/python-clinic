import React from 'react'

import { mount} from 'enzyme'
import { MemoryRouter } from 'react-router-dom'
import {Provider} from 'react-redux'

import configureStore from 'redux-mock-store'

import NotFound from 'python-clinic/pages/NotFound'

describe('NotFound',()=>{
    const initialState = {}
    const mockStore = configureStore()
    let store
    let view

    beforeEach(()=>{
        store = mockStore(initialState)
    })

    it('should render a header ', () => {
        view = mount((
            <MemoryRouter>
                <Provider store={store}>
                    <NotFound />
                </Provider>
            </MemoryRouter>
        ))

        expect(view.text()).to.match(/404\s*Page Not Found/)
    })
})
