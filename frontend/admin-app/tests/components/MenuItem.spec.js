import React from 'react'

import { mount} from 'enzyme'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { Redirect } from 'react-router-dom'

import configureStore from 'redux-mock-store'
import * as Feather from 'react-feather'

import MenuItem from 'python-clinic/SideBar/MenuItem'


describe('MenuItem', ()=>{
    const initialState = {}
    const mockStore = configureStore()
    let store
    let view

    beforeEach(()=>{
        store = mockStore(initialState)
    })

    it('should render a <li class="nav-item">', () => {

        view = mount((
            <MemoryRouter>
                <Provider store={store}>
                    <MenuItem name="Item One" to="/foo/bar" />
                </Provider>
            </MemoryRouter>
        ))

        expect(view.html()).to.equal('<li class="nav-item"><a class="text-secondary d-flex mt-2 mb-2" aria-current="false" href="/foo/bar"> &nbsp; Item One</a></li>')
    })
    it('should render a FontAwesomeIcon if given one', () => {

        view = mount((
            <MemoryRouter>
                <Provider store={store}>
                    <MenuItem name="Item One" to="/foo/bar" icon={Feather.Truck} />
                </Provider>
            </MemoryRouter>
        ))

        expect(view.find(Feather.Truck).length).to.equal(1)
    })

})
