odoo.define('record_authenticate_by_user.main', function (require) {
    "use strict";
    var FormController = require('web.FormController');
    var session = require('web.session');
    var rpc = require('web.rpc');
    
    FormController.include({
    	_onSave: function (ev) {
	        var self = this;
	        var model = self.modelName;
			var passkey = ""
			var locale = {
			    OK: 'Confirm',
			    CONFIRM: 'Confirm',
			    CANCEL: 'Cancel'
			};
			rpc.query({
                model: 'record.authenticate',
                method: 'check_model',
                args: [model],
            })
            .then(function (result) {
            	if(result == '1'){
            		var form_content = "<form class='form'>" +
						    		        "<div class='form-group'>" +
						    		          "<label for='password'>Password</label>" +
						    		          "<input type='password' class='form-control' id='c_password' name='password' placeholder='Enter your password'/>" +
						    		        "</div>" +
						    		        "<div class='checkbox'>" +
						    		          "<label>" +
						    		            "<input id='close_status' type='checkbox' checked='checked'/>&nbsp; Is record status needs to be closed ?" +
						    		          "</label>" +
						    		        "</div>" +
						    		      "</form>";
        		    var modal = bootbox.dialog({
        		        message: form_content,
        		        title: "Confirm your account to update the record",
        		        buttons: [
        		          {
        		            label: "Save",
        		            className: "btn btn-primary pull-left",
        		            callback: function() {
        		                var passkey = $('#c_password').val();
        		                var close_status = $('#close_status').prop('checked');
								rpc.query({
								    model: 'record.authenticate',
								    method: 'autenticate_user',
								    args: [session.origin, session.db, session.username, passkey, model],
								})
								.then(function (result) {
									if(result == '1'){
										ev.stopPropagation(); // Prevent x2m lines to be auto-saved
										self.saveRecord();
										
										var action_close_status = function(){
											var record_id = self.el.baseURI.split('#id=').pop().split('&')[0];
//											console.log(self, self.el.baseURI, record_id,"---------ID-------------");
											if(close_status){
	//												alert("close status update true needs")
												rpc.query({
												    model: 'record.authenticate',
												    method: 'action_close_status',
												    args: [record_id, model],
												})
//												location.reload(); 
											}
										};
										setTimeout(action_close_status, 1000);
										

										
//										console.log(sar, self ,"SSSSAAAAARRRRR");
										modal.modal("hide");
									}else{
										alert("User validation failured. Please try again.");
										modal.modal("hide");
									}
								});
								
        		                return false;
        		            }
        		          },
        		          {
        		            label: "Close",
        		            className: "btn btn-default pull-left",
        		            callback: function() {
        		              console.log("Modal is on closing");
        		            }
        		          }
        		        ],
        		        show: false,
        		        onEscape: function() {
        		          modal.modal("hide");
        		        }
        		    });
        		    
        		    modal.modal("show");
            	}else{
            		ev.stopPropagation(); // Prevent x2m lines to be auto-saved
            		self.saveRecord();
            	}
            });
	    },
	});
});