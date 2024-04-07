#implementação de um servidor base para interpratação de métodos HTTP

import socket
import codecs

#definindo o endereço IP do host
SERVER_HOST = ""
#definindo o número da porta em que o servidor irá escutar pelas requisições HTTP
SERVER_PORT = 80

#vamos criar o socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#vamos setar a opção de reutilizar sockets já abertos
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#atrela o socket ao endereço da máquina e ao número de porta definido
server_socket.bind((SERVER_HOST, SERVER_PORT))

#coloca o socket para escutar por conexões
server_socket.listen(1)

#mensagem inicial do servidor
print("Servidor em execução...")
print("Escutando por conexões na porta %s" % SERVER_PORT)

#cria o while que irá receber as conexões
while True:
    #espera por conexões
    #client_connection: o socket que será criado para trocar dados com o cliente de forma dedicada
    #client_address: tupla (IP do cliente, Porta do cliente)
    client_connection, client_address = server_socket.accept()

    #pega a solicitação do cliente
    request = client_connection.recv(1024)
    while True:
        if len(request) == 1024:
            request += client_connection.recv(1024)
        else:
            break
    request = request.decode()

    #verifica se a request possui algum conteúdo (pois alguns navegadores ficam periodicamente enviando alguma string vazia)
    if request:
        #imprime a solicitação do cliente
        #print(request)
        
        #analisa a solicitação HTTP
        headers = request.split("\n")
        #print(headers)#impressão dos cabeçalhos
        http_request = headers[0].split()
        #pega o método do arquivo sendo solicitado
        method = http_request[0]
        #pega o nome do arquivo sendo solicitado
        file_name = http_request[1]
        file = []
        file_type = ""

        if method == "GET":
            #verifica qual arquivo está sendo solicitado e envia a resposta para o cliente
            if file_name == "/":
                file_name = "/index.html"
            else:
                # verifica se existe . no arquivo e separa o nome do tipo do arquivo
                if file_name.find(".") != -1:
                    file = file_name.split(".")
                    file_type = file[1]

            #try e except para tratamento de erro quando um arquivo solicitado não existir
            try:
                #abrir o arquivo e enviar para o cliente
                if file_type != "txt":
                    fin = open("htdocs" + file_name, "rb")
                else:
                    fin = open("htdocs" + file_name)
                #leio o conteúdo do arquivo para uma variável
                content = fin.read()
                #fecho o arquivo
                fin.close()
                #envia a resposta
                if file_type != "txt":
                    response = b"HTTP/1.1 200 OK\n\n" + content + b"\n\n"
                else:
                    response = "HTTP/1.1 200 OK\n\n" + content + "\n\n"
            except FileNotFoundError:
                #caso o arquivo solicitado não exista no servidor, gera uma resposta de erro
                response = "HTTP/1.1 404 NOT FOUND\n\n<h1>ERROR 404!<br>File Not Found!</h1>\n\n"
        elif method == "PUT":
            file_name = file_name.replace("/","")
            try:
                new_item = open("htdocs/" + file_name, "x")
                payload = ""
                for i in headers:
                    if i == "\r":
                        start = headers.index(i)
                for i in range(len(headers)):
                    if start < i:
                        payload = payload + headers[i] + "\n"
                new_item.write(payload)
                new_item.close()        
                with open("htdocs/index.html", "r") as f:
                    index_lines = f.readlines()
                    for i in index_lines:
                        if "</body>" in i:
                            new_line_index = index_lines.index(i)-1
                with open("htdocs/index.html", "r") as f:
                    index_lines = f.readlines()
                with open("htdocs/index.html", "w") as f:
                    for i in index_lines:
                        if index_lines.index(i) == new_line_index:
                            f.write(i + "\t<p>Here's a link to <a href=" + file_name + ">" + file_name + "</a></p>\n")
                        else:
                            f.write(i)    
            except FileExistsError:
                item = open("htdocs/" + file_name, "w")
                #item_content = item.read()
                payload = ""
                for i in headers:
                    if i == "\r":
                        start = headers.index(i)
                for i in range(len(headers)):
                    if start < i:
                        payload = payload + headers[i] + "\n"
                item.write(payload)
                item.close()
                
            response = "HTTP/1.1 200 OK\n\n" 
        else:
            #caso o método solicitado não exista no servidor, gera uma resposta de erro
            response = "HTTP/1.1 501 NOT IMPLEMENTED\n\n<h1>ERROR 501!<br>Method Not Implemented!</h1>\n\n"
        #envia a resposta HTTP
        if method == "GET" and file_type !="txt" and response != "HTTP/1.1 404 NOT FOUND\n\n<h1>ERROR 404!<br>File Not Found!</h1>\n\n":
            client_connection.sendall(response)
        else:
            client_connection.sendall(response.encode())

        client_connection.close()

server_socket.close()