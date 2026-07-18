$(document).ready(function () {
  const searchInput = $('#search-orders');
  const resultsContainer = $('#orders-container');
  const emptyState = $('#frontdesk-empty-state');
  const loadingState = $('#frontdesk-loading-state');
  let requestToken = 0;

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop().split(';').shift();
    }
    return '';
  }

  const csrfToken = getCookie('csrftoken');

  function orderBadge(status) {
    if (status === 'Delivered') {
      return '<span class="badge bg-success">Delivered</span>';
    }
    if (status === 'Processing') {
      return '<span class="badge bg-warning text-dark">Processing</span>';
    }
    return '<span class="badge bg-secondary">Pending</span>';
  }

  function renderOrders(orders) {
    resultsContainer.empty();

    if (!orders.length) {
      emptyState.removeClass('d-none');
      return;
    }

    emptyState.addClass('d-none');

    orders.forEach(function (order) {
      const confirmButton = order.order_status === 'Delivered'
        ? '<button type="button" class="btn btn-sm btn-outline-success w-100" disabled>Confirmed</button>'
        : order.order_status === 'Processing'
        ? `
          <button
            type="button"
            class="btn btn-sm btn-orange w-100 mark-delivered-btn"
            data-delivered-url="${order.delivered_url}"
            data-order-id="${order.order_id}"
          >
            Mark Delivered
          </button>
        `
        : `
          <form method="post" action="${order.confirm_url}">
            <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
            <button type="submit" class="btn btn-sm btn-orange w-100">Confirm</button>
          </form>
        `;

      const orderCard = `
        <article class="frontdesk-order-simple">
          <div class="frontdesk-order-simple-top">
            <div>
              <p class="frontdesk-order-id">Order #${order.order_id}</p>
              <h4>${order.customer}</h4>
              <p class="frontdesk-order-meta">${order.email || 'No email'}</p>
            </div>
            <div class="frontdesk-order-badges">
              ${orderBadge(order.order_status)}
              <span class="qty-pill">${order.payment_status}</span>
            </div>
          </div>

          <div class="frontdesk-order-simple-grid">
            <div>
              <span>Created</span>
              <strong>${order.date}</strong>
            </div>
            <div>
              <span>Pickup</span>
              <strong>${order.pick_up_date}</strong>
            </div>
            <div>
              <span>Total</span>
              <strong>&#8358;${order.total}</strong>
            </div>
            <div>
              <span>Items</span>
              <strong>${order.item_count}</strong>
            </div>
          </div>

          <div class="frontdesk-order-simple-actions">
            <a href="${order.detail_url}" class="btn btn-outline-light btn-sm w-100">View</a>
            ${confirmButton}
          </div>
        </article>
      `;

      resultsContainer.append(orderCard);
    });
  }

  function loadOrders(query) {
    const currentToken = ++requestToken;

    loadingState.removeClass('d-none');

    $.ajax({
      url: '/frontdesk/search-orders/',
      method: 'GET',
      data: { q: query },
      success: function (response) {
        if (currentToken !== requestToken) {
          return;
        }

        loadingState.addClass('d-none');
        renderOrders(response.orders || []);
      },
      error: function () {
        if (currentToken !== requestToken) {
          return;
        }

        loadingState.addClass('d-none');
        emptyState.removeClass('d-none').text('Unable to load orders right now.');
      }
    });
  }

  $(document).on('click', '.mark-delivered-btn', function () {
    const button = $(this);
    const deliveredUrl = button.data('delivered-url');
    const orderId = button.data('order-id');

    Swal.fire({
      title: 'Mark delivered?',
      text: `Confirm that order #${orderId} has been delivered.`,
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'Yes, deliver it',
      cancelButtonText: 'Cancel',
      confirmButtonColor: '#EA580C',
      cancelButtonColor: '#64748b',
    }).then(function (result) {
      if (!result.isConfirmed) {
        return;
      }

      $.ajax({
        url: deliveredUrl,
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
        },
        beforeSend: function () {
          button.prop('disabled', true).text('Updating...');
        },
        success: function (response) {
          Swal.fire({
            icon: 'success',
            title: response.message || 'Order updated',
            timer: 1800,
            showConfirmButton: false,
          });
          loadOrders(searchInput.val().trim());
        },
        error: function (xhr) {
          let errorMessage = 'Unable to update order.';
          try {
            const parsed = JSON.parse(xhr.responseText);
            errorMessage = parsed.message || errorMessage;
          } catch (error) {}

          Swal.fire({
            icon: 'error',
            title: 'Update failed',
            text: errorMessage,
          });
          button.prop('disabled', false).text('Mark Delivered');
        }
      });
    });
  });

  if (searchInput.length && resultsContainer.length) {
    loadOrders(searchInput.val().trim());

    let debounceTimer;
    searchInput.on('input', function () {
      clearTimeout(debounceTimer);
      const query = $(this).val().trim();
      debounceTimer = setTimeout(function () {
        loadOrders(query);
      }, 200);
    });
  }
});
