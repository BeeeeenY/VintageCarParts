<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Vintage Car</title>

    <style>
        .category {
            font-weight:bolder;
            font-size: large;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Navigation Bar -->
        <div class="row justify-content-between">
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <span class="navbar-brand mb-0 h1">VintageCar</span>
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
                  <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
                  <div class="navbar-nav">
                    <a class="nav-item nav-link active" href="#">Home</a>
                    <a class="nav-item nav-link" href="#">Car Parts</a>
                    <a class="nav-item nav-link" href="#">Others</a>
                  </div>
                </div>
                <div class="navbar-nav">
                    <a class="nav-item nav-link" href="#">Register</a>
                    <a class="nav-item nav-link" href="#">Login</a>
                </div>
                <form class="form-inline">
                    <button class="btn btn-outline-danger" type="button">Buy</button>
                </form>
            </nav>
        </div>

        <div class="row mb-4"></div>
    </div>

    <div class="container">
        <div class="row">
            <div style="font-weight: bolder; font-size: x-large; text-align: center;">Order Detail</div>
        </div>
    </div>

    <div class="container">
        <table class="table table-bordered">
            <tr>
                <th>OrderID</th>
                <td>{{order.OrderID}}</td>
            </tr>
            <tr>
                <th>BuyerID</th>
                <td>{{order.BuyerID}}</td>
            </tr>
            <tr>
                <th>Purchased Date</th>
                <td>{{order.Purchaseddate}}</td>
            </tr>
            <tr>
                <th>Quantity</th>
                <td>{{order.Quantity}}</td>
            </tr>
            <tr>
                <th>Total Price</th>
                <td>{{order.TotalPrice}}</td>
            </tr>
        </table>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</body>
</html>
