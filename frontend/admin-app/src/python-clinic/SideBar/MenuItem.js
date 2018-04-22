import React from "react"
import { NavLink } from 'react-router-dom'
import {ComponentWithStore} from 'python-clinic/utils/ui'

const MenuItem = ({ name, to, icon=null, iconSrc=null, target=null, width=32, height=32 }) => {
    const fallbackIcon = iconSrc ? <img src={iconSrc} alt={name} width={width} height={height} />: null
    const Icon = icon
    return (
        <li className="nav-item">
            <NavLink exact to={to} target={target} className="text-secondary d-flex mt-2 mb-2" activeClassName="text-warning">
                {icon ? <Icon /> : fallbackIcon} &nbsp; {name}
            </NavLink>
        </li>
    )
}
export default ComponentWithStore(MenuItem)
