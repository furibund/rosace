# rosace
Animated mandala-like floral ornament

This websocket server provides the client with an animated floral mandala.
As the mandala is created and managed by the server, each client sees the same rosace.

Start the server with:  python[3] rosace-app.py


rosace-app.py options:

  --morph_interval                 interval of morphing (default 5000)
  
  --number_of_corollas             number of corollas (default 6)
  
  --number_of_petals               number of petals of outer corolla (default 24)
  
  --port                           run on the given port (default 9000)
  
  --root_dir                       DOCUMENT_ROOT (default $(app's working directory)) <b> experimental</b>
  
