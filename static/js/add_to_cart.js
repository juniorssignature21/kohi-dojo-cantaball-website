import Swal from './sweetalert2.esm.all.min.js';

const cartIcon = ` <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 456.029 456.029" style="enable-background:new 0 0 456.029 456.029;" xml:space="preserve">
                        <g>
                          <g>
                            <path d="M345.6,338.862c-29.184,0-53.248,23.552-53.248,53.248c0,29.184,23.552,53.248,53.248,53.248
                         c29.184,0,53.248-23.552,53.248-53.248C398.336,362.926,374.784,338.862,345.6,338.862z" />
                          </g>
                        </g>
                        <g>
                          <g>
                            <path d="M439.296,84.91c-1.024,0-2.56-0.512-4.096-0.512H112.64l-5.12-34.304C104.448,27.566,84.992,10.67,61.952,10.67H20.48
                         C9.216,10.67,0,19.886,0,31.15c0,11.264,9.216,20.48,20.48,20.48h41.472c2.56,0,4.608,2.048,5.12,4.608l31.744,216.064
                         c4.096,27.136,27.648,47.616,55.296,47.616h212.992c26.624,0,49.664-18.944,55.296-45.056l33.28-166.4
                         C457.728,97.71,450.56,86.958,439.296,84.91z" />
                          </g>
                        </g>
                        <g>
                          <g>
                            <path d="M215.04,389.55c-1.024-28.16-24.576-50.688-52.736-50.688c-29.696,1.536-52.224,26.112-51.2,55.296
                         c1.024,28.16,24.064,50.688,52.224,50.688h1.024C193.536,443.31,216.576,418.734,215.04,389.55z" />
                          </g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                        <g>
                        </g>
                      </svg>`

$(document).ready(function() {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
    });

    function generateCartId() {
        let cartId = localStorage.getItem('cartId');
        if (!cartId) {
            cartId = Array.from({ length: 10 }, () => Math.floor(Math.random() * 10)).join('');
            localStorage.setItem('cartId', cartId);
        }
        return cartId;
    }

    function syncCartCount() {
        const cart_id = localStorage.getItem('cartId');
        if (cart_id) {
            $.ajax({
                url: '/get-cart-count/',
                method: 'GET',
                data: { 'cart_id': cart_id },
                success: function(response) {
                    $('.total_cart_items').text(response?.total_cart_items || 0);
                    $('.price').text(`₦ ${response?.cart_sub_total || '0.00'}`);
                    $('.total_price').text(`₦ ${response?.total_price || '0.00'}`);
                }
            });
        }
    }

    syncCartCount();

    $(document).on('click', '.add-to-cart-btn', function() {
        const button_el = $(this);
        const id = button_el.attr('data-id');
        const qty = parseInt(button_el.attr('data-qty')) || 1;
        const cart_id = generateCartId();

        $.ajax({
            url: '/add-to-cart/',
            data: {
                'id': id,
                'qty': qty,
                'cart_id': cart_id,
            },
            beforeSend: function() {
                button_el.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="color:white;"></span>');
                button_el.prop('disabled', true);
            },
            success: function(response) {
                Toast.fire({
                    icon: 'success',
                    title: response.message,
                });
                button_el.html(cartIcon);
                button_el.prop('disabled', false);

                $('.total_cart_items').text(response?.total_cart_items || 0);
                $('.price').text(`₦ ${response?.cart_sub_total || '0.00'}`);
                $('.total_price').text(`₦ ${response?.total_price || '0.00'}`);
                location.reload();
            },
            error: function(xhr) {
                let errorResponse = { error: 'Unable to add item to cart.' };
                try {
                    errorResponse = JSON.parse(xhr.responseText);
                } catch (e) {}

                Toast.fire({
                    icon: 'error',
                    title: errorResponse?.error || 'Unable to add item to cart.',
                });
                button_el.html(cartIcon);
                button_el.prop('disabled', false);
            }
        });
    });

    $(document).on('click', '.qtybtn', function() {
        const button_el = $(this);
        const item_id = button_el.attr('data-item-id');
        const input_el = $('input.item-qty-' + item_id);
        let qty = parseInt(input_el.val(), 10) || 1;
        const product_id = button_el.attr('data-product-id');
        const cart_id = generateCartId();
        const stock = parseInt(input_el.attr('data-qty'), 10) || 100;

        if (button_el.hasClass('inc')) {
            qty = Math.min(qty + 1, stock);
        } else if (qty > 1) {
            qty -= 1;
        }

        input_el.val(qty);

        $.ajax({
            url: '/add-to-cart/',
            data: {
                id: product_id,
                qty: qty,
                cart_id: cart_id,
            },
            success: function(response) {
                Toast.fire({
                    icon: 'success',
                    title: response?.message,
                });

                $('.price').text(`₦ ${response.cart_sub_total}`);
                $('.total_price').text(`₦ ${response.total_price}`);
                location.reload();
            },
            error: function(xhr) {
                let errorResponse = { error: 'Unable to update cart.' };
                try {
                    errorResponse = JSON.parse(xhr.responseText);
                } catch (e) {}

                Toast.fire({
                    icon: 'error',
                    title: errorResponse?.error || 'Unable to update cart.',
                });
                input_el.val(stock);
            }
        });
    });

    $(document).on('click', '.delete_cart_item', function() {
        const button_el = $(this);
        const item_id = button_el.attr('data-item-id');
        const product_id = button_el.attr('data-product-id');
        const cart_id = generateCartId();

        $.ajax({
            url: '/delete-cart-item/',
            data: {
                id: product_id,
                item_id: item_id,
                cart_id: cart_id,
            },
            beforeSend: function() {
                button_el.html('<i class="fa fa-spinner fa-spin ms-2"></i>');
            },
            success: function(response) {
                Toast.fire({
                    icon: 'success',
                    title: response?.message,
                });
                $('.total_cart_items').text(response?.total_cart_items || 0);
                $('.price').text(`₦ ${response?.cart_sub_total || '0.00'}`);
                $('.total_price').text(`₦ ${response?.total_price || '0.00'}`);
                $('.cart-item').filter(function() {
                    return $(this).find('[data-item-id="' + item_id + '"]').length;
                }).remove();
                location.reload();
            }
        });
    });
});
