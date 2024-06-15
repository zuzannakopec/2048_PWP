$(document).ready(function() {
    $.post('/initialize_game', function(data) {
        updateBoard(data.board);
    });

    $(document).keydown(function(e) {
        let direction;
        switch(e.which) {
            case 37: direction = 'left'; break;
            case 38: direction = 'up'; break;
            case 39: direction = 'right'; break;
            case 40: direction = 'down'; break;
            default: return;
        }
        $.ajax({
            url: '/move',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ direction: direction }),
            success: function(data) {
                updateBoard(data.board);
            }
        });
    });
});

function updateBoard(board) {
   console.log(JSON.stringify(board))
    let html = '<table>';
    for (let i = 0; i < board.length; i++) {
        html += '<tr>';
        for (let j = 0; j < board[i].length; j++) {
            let tileValue = board[i][j];
            let tileClass = tileValue === 0 ? 'empty' : `tile-${tileValue}`;
            html += `<td class="${tileClass}">${tileValue !== 0 ? tileValue : ''}</td>`;
        }
        html += '</tr>';
    }
    html += '</table>';
    $('#board').html(html);
}

function getCurrentBoardState() {
    let boardState = [];
    $('#board tr').each(function() {
        let row = [];
        $(this).find('td').each(function() {
            let value = parseInt($(this).text()) || 0;
            row.push(value);
        });
        boardState.push(row);
    });
    return boardState;
}
