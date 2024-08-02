$( document ).ready(function() {

    $('#like-form').submit(function(e){
        e.preventDefault()

        const post_id = $(this).attr('elementID')
        const url = $(this).attr('action')

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'post_id':post_id,
            },
            dataType: 'json',
            success: function(response) {
                $(`#likes_count${post_id}`).text(response['amount_likes'])
            },

            error: function(response) {
                alert('An error has occurred while liking a post!')
            }
        })

    })
});
