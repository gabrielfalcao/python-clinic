import React from "react"
import ContainerRight from 'python-clinic/components/ContainerRight'
import logo from 'python-clinic/logo.png'
import TITLE from 'python-clinic/constants'

export class NotFound extends React.Component {
    render() {
        return (
            <ContainerRight title={"Login"} className="container-fluid col-lg-12">
                <div className="login-page">
                    <div className="form-signin col-md-6 col-sm-12">
                        <h1>404</h1>
                        <p>
                            <br />
                            <br />
                            <br />
                            <img id="python-clinic-logo" src={logo} className="img-fluid" alt={TITLE}/>
                            <br />
                            <br />
                            <br />
                        </p>

                        <h3>Page Not Found</h3>
                    </div>
                </div>
            </ContainerRight>
        )
    }
}



export default NotFound
