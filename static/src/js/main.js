odoo.define('record_authenticate_by_user.main', function (require) {
    "use strict";
    var FormController = require('web.FormController');
    var session = require('web.session');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;
    
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
						    		          "<input type='password' class='form-control' id='c_password' name='password' placeholder='Enter your password' onkeypress='if (event.keyCode === 13) { event.preventDefault(); }'/>" +
						    		        "</div>" +
						    		        "<div class='form-group'>" +
						    		            "<label>Is record status needs to be closed ?</label> &nbsp; " +
						    		            "<input id='close_status' type='checkbox' checked='checked' onkeypress='if (event.keyCode === 13) { event.preventDefault(); }'/>" +
						    		        "</div>" +
						    		      "</form>";
        		    var modal = bootbox.dialog({
        		        message: form_content,
        		        title: "Confirm your account to update the record",
        		        buttons: [
        		          {
        		            label: "Approve",
        		            className: "btn btn-primary pull-left",
        		            callback: function() {
        		                var passkey = $('#c_password').val();
        		                var close_status = $('#close_status').prop('checked');
								rpc.query({
								    model: 'record.authenticate',
								    method: 'autenticate_user',
								    args: [session.origin, session.db, session.username, passkey, model],
								}).then(function (result) {
									if(result == '1'){
										ev.stopPropagation(); // Prevent x2m lines to be auto-saved
										self.renderer.state.data.state = "closed";
										self.saveRecord();
//										action for status close(checkbox)
										var action_close_status = function(){
											var record_id = self.renderer.state.data.id;
											if(close_status){
												rpc.query({
												    model: 'record.authenticate',
												    method: 'action_close_status',
												    args: [record_id, model],
												}).then(function (result){
													self.reload();
												})
												 
											}
										};
										setTimeout(action_close_status, 2000);
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
	    saveRecord: function () {
	        var self = this;
	        return this._super.apply(this, arguments).then(function (changedFields) {
	            // the title could have been changed
	            self.renderer.state.data.state = "closed";
	            self.set('title', self.getTitle());
	            self._updateEnv();
	            if (_t.database.multi_lang && changedFields.length) {
	                // need to make sure changed fields that should be translated
	                // are displayed with an alert
	                var fields = self.renderer.state.fields;
	                var data = self.renderer.state.data;
	                var alertFields = [];
	                for (var k = 0; k < changedFields.length; k++) {
	                    var field = fields[changedFields[k]];
	                    var fieldData = data[changedFields[k]];
	                    if (field.translate && fieldData) {
	                        alertFields.push(field);
	                    }
	                }
	                if (alertFields.length) {
	                    self.renderer.displayTranslationAlert(alertFields);
	                }
	            }
	            return changedFields;
	        });
	    },
	    _update: function () {
	        var title = this.getTitle();
	        this.set('title', title);
	        this.set('state', 'closed');
	        this._updateButtons();
	        this._updateSidebar();
	        return this._super.apply(this, arguments).then(this.autofocus.bind(this));
	    },
	    _setMode: function (mode, recordID) {
	        if ((recordID || this.handle) === this.handle) {
	            this.model.unfreezeOrder(this.handle);
	        }
	        return this._super.apply(this, arguments);
	    },
	});
    
    
});


