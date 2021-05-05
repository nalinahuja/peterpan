import os

# End Imports---------------------------------------------------------------------------------------------------------------------------------------------------------------

def navbar(request):
    # Set Default Navbar Fields
    href, outline, text = "/login", "primary", "Login"

    # Update Navbar Fields
    if (request.cookies.get('access_token_cookie')):
        href, outline, text = "/logoff", "danger", "Logoff"

    # Return Navbar To Caller
    return """
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
            <nav class="navbar sticky-top navbar-expand-lg navbar-light bg-light">
              <a class="navbar-brand" href="#">
                Peterpan
              </a>
              <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
              </button>

              <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav mr-auto">
                  <li class="nav-item active">
                    <a class="nav-link" href="/">Home<span class="sr-only">(current)</span></a>
                  </li>
                  <li class="nav-item active">
                    <a class="nav-link" href="/stocks">Stocks</a>
                  </li>
                  <li class="nav-item active">
                    <a class="nav-link" href="/buy">Buy</a>
                  </li>
                  <li class="nav-item active">
                    <a class="nav-link" href="/sell">Sell</a>
                  </li>
                  <li class="nav-item active">
                    <a class="nav-link" href="/portfolio">Portfolio</a>
                  </li>
                </ul>

                <form method="POST" action="/" class="form-inline my-2 my-lg-0">
                  <input class="form-control mr-sm-2" type="text" placeholder="Stock name..." aria-label="Search" name="search_info"  id="search_info">
                  <button class="btn btn-outline-success my-2 my-sm-0" type="submit" name="search" value="search">Search</button>
                </form>

                <div style="padding-left: 10px;"><div>

                <ul class="navbar-nav">
                  <li class="nav-item active">
                    <a href="{}"><button type="button" class="btn btn-outline-{}">{}</button></a>
                  </li>
                </ul>
              </div>
            </nav>
           """.format(href, outline, text)

# End File---------------------------------------------------------------------------------------------------------------------------------------------------------------
