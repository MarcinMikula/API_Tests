from flask import Flask, request, Response
import xml.etree.ElementTree as ET

app = Flask(__name__)


# Prosty endpoint SOAP
@app.route('/soap/', methods=['POST'])
def soap_service():
    # Pobierz treść żądania SOAP
    soap_request = request.data.decode('utf-8')

    # Parsuj XML żądania
    root = ET.fromstring(soap_request)

    # Znajdź nazwę operacji
    body = root.find('.//{http://schemas.xmlsoap.org/soap/envelope/}Body')
    operation = list(body)[0].tag.split('}')[-1]  # Pobierz nazwę operacji (np. GetProduct)

    # Przygotuj odpowiedź w zależności od operacji
    if operation == "GetProduct":
        product_id = body.find('.//id').text
        response_data = f"{{'id': {product_id}, 'name': 'Laptop', 'description': 'Laptop gamingowy'}}"
        soap_response = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <GetProductResponse xmlns="http://example.com/soap">
                    <result>{response_data}</result>
                </GetProductResponse>
            </soap:Body>
        </soap:Envelope>
        """
        return Response(soap_response, mimetype='text/xml', status=200)

    elif operation == "CreateProduct":
        response_data = 21
        soap_response = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <CreateProductResponse xmlns="http://example.com/soap">
                    <result>{response_data}</result>
                </CreateProductResponse>
            </soap:Body>
        </soap:Envelope>
        """
        return Response(soap_response, mimetype='text/xml', status=201)

    elif operation == "DeleteProduct":
        response_data = "{'status': 'Product deleted'}"
        soap_response = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <DeleteProductResponse xmlns="http://example.com/soap">
                    <result>{response_data}</result>
                </DeleteProductResponse>
            </soap:Body>
        </soap:Envelope>
        """
        return Response(soap_response, mimetype='text/xml', status=204)

    else:
        soap_response = """
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <soap:Fault>
                    <faultcode>soap:Client</faultcode>
                    <faultstring>Invalid operation</faultstring>
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
        """
        return Response(soap_response, mimetype='text/xml', status=400)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8002, debug=True)
    print("SOAP server running on http://127.0.0.1:8002/soap/")