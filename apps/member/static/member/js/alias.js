
 $("#alias_input").on('keypress',function(e) {
     if(e.which == 13) {
         $("#alias_submit").click();
     }
 });

 function create_alias(note_id){
     $.post("/api/note/alias/",
            {
                "csrfmiddlewaretoken": CSRF_TOKEN,
                "name": $("#alias_input").val(),
                "note": note_id
            }
     ).done(function(){
         $("#alias_table").load(location.pathname+ " #alias_table");
         addMsg("Alias ajouté","success");
     })
      .fail(function(xhr, textStatus, error){
          errMsg(xhr.responseJSON);
      });
}
 // on click of button "delete" , call the API
 function delete_button(button_id){
     $.ajax({
         url:"/api/note/alias/"+button_id+"/",
         method:"DELETE",
         headers: {"X-CSRFTOKEN": CSRF_TOKEN}
     })
      .done(function(){
          addMsg('Alias supprimé','success');
          $("#alias_table").load(location.pathname + " #alias_table");
      })
      .fail(function(xhr,textStatus, error){
          errMsg(xhr.responseJSON);
      });
 }
