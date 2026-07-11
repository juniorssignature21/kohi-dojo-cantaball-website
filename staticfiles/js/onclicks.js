import Swal from './sweetalert2.esm.all.min.js';

$(document).ready(function() {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
        });
    
        $(document).on('click', '#mark-as-played', function() {
            const button_el = $(this);
            const id = button_el.attr('data-id');
        
            $.ajax({
                url:'/mark-as-played/',
                data:{
                    'pk':id
                },
                beforeSend: function(){
                    button_el.html('Marking...');
                    button_el.prop('disabled', true)
                },
                success: function(response) {
                    console.log(response);
        
                    Toast.fire({
                        icon: 'success',
                        title: response.message,
                    });
                    button_el.html('Mark As Played');
                    button_el.prop('disabled', false);
        
                },
                error: function(xhr, status, error) {
                    console.error("Error Status:", xhr.status);
                    console.error("Error Response:", xhr.responseText);
                    let errorMessage = 'Unable to mark match as played.';

                    try {
                        const errorResponse = JSON.parse(xhr.responseText);
                        errorMessage = errorResponse?.error || errorMessage;
                    } catch (parseError) {
                        errorMessage = xhr.statusText || error || errorMessage;
                    }
        
                    Toast.fire({
                        icon: 'error',
                        title: errorMessage,
                    });
                    button_el.html('Mark As Played');
                    button_el.prop('disabled', false);
                }
            })
        })
})
