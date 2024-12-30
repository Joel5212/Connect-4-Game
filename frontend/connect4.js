var currPlayer = "X"
var gameOver = false;
var board;
var currColumns;
var colIndex;
var gameStatus;
var prevComputerTile;
var winningPieces;

var rowLength = 6
var colLength = 7

var playerScore = 0
var computerScore = 0

window.onload = function () {
    setGame()
}

function setGame() {

    board = []
    currColumns = [5, 5, 5, 5, 5, 5, 5]

    for (let rowIndex = 0; rowIndex < rowLength; rowIndex++) {
        let row = []
        for (let colIndex = 0; colIndex < colLength; colIndex++) {
            //JS
            row.push("-")

            //HTML
            let tile = document.createElement("div");
            tile.id = rowIndex.toString() + "-" + colIndex.toString()
            tile.classList.add("tile");
            tile.addEventListener("click", movePiece)
            document.getElementById("board").append(tile);
        }
        board.push(row)
    }

    document.getElementById("player-score").textContent = playerScore
    document.getElementById("computer-score").textContent = computerScore
}

function movePiece() {

    if (gameOver || (this.id && currPlayer == "O")) {
        return;
    }

    if (currPlayer === "X") {
        let coords = this.id.split("-")
        colIndex = parseInt(coords[1]);
    }

    rowIndex = currColumns[colIndex];

    if (rowIndex < 0) {
        return;
    }

    board[rowIndex][colIndex] = currPlayer

    let tile = document.getElementById(rowIndex.toString() + "-" + colIndex.toString());

    if (currPlayer == "O") {
        if (prevComputerTile) {
            prevComputerTile.classList.remove("recent-yellow-piece")
        }
        prevComputerTile = tile
    }

    rowIndex -= 1
    currColumns[colIndex] = rowIndex;

    if (currPlayer === "X") {
        tile.classList.add("red-piece")
    }
    else {
        tile.classList.add("yellow-piece")
        tile.classList.add("recent-yellow-piece")
    }

    checkForWinner()

    if (!gameOver) {
        if (currPlayer === "X") {
            currPlayer = "O"
            computerMove(board)
        } else if (currPlayer === "O") {
            currPlayer = "X"
        }
    }
}

function computerMove(board) {

    fetch('http://127.0.0.1:2000/retrieve-computer-move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(board)
    }).then(response => {
        if (!response.ok) {
            throw new Error('Issue with network response');
        }
        return response.json();
    }).then(data => {
        let computer_move_status_winning_pieces = data.computer_move_status_winning_pieces
        colIndex = computer_move_status_winning_pieces[0]
        gameStatus = computer_move_status_winning_pieces[1]
        winningPieces = computer_move_status_winning_pieces[2]
        movePiece()
    }).catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function checkGameStatus(board) {

    let totalNonEmptyCount = 0

    playerPiece = "X"
    computerPiece = "O"

    for (let i = 0; i < board[0].length; i++) {
        for (let j = 0; j < board[0].length; j++) {

            if (j < 4 && i < 6) {
                rowValOneHorizontal = board[i][j]
                rowValTwoHorizontal = board[i][j + 1]
                rowValThreeHorizontal = board[i][j + 2]
                rowValFourHorizontal = board[i][j + 3]

                if (j == 0) {
                    if (rowValOneHorizontal != "-") {
                        totalNonEmptyCount += 1
                    }
                    if (rowValTwoHorizontal != "-") {
                        totalNonEmptyCount += 1
                    }
                    if (rowValThreeHorizontal != "-") {
                        totalNonEmptyCount += 1
                    }
                    if (rowValFourHorizontal != "-") {
                        totalNonEmptyCount += 1
                    }
                }
                else {
                    if (rowValFourHorizontal != "-") {
                        totalNonEmptyCount += 1
                    }
                }

                if (computerPiece == rowValOneHorizontal && rowValOneHorizontal == rowValTwoHorizontal && rowValTwoHorizontal == rowValThreeHorizontal && rowValThreeHorizontal == rowValFourHorizontal) {
                    winningPieces = [[i, j], [i, j + 1], [i, j + 2], [i, j + 3]]
                    return 1
                }
                if (playerPiece == rowValOneHorizontal && rowValOneHorizontal == rowValTwoHorizontal && rowValTwoHorizontal == rowValThreeHorizontal && rowValThreeHorizontal == rowValFourHorizontal) {
                    winningPieces = [[i, j], [i, j + 1], [i, j + 2], [i, j + 3]]
                    return -1
                }
            }

            if (j < 3) {
                rowValOneVertical = board[j][i]
                rowValTwoVertical = board[j + 1][i]
                rowValThreeVertical = board[j + 2][i]
                rowValFourVertical = board[j + 3][i]

                if (computerPiece == rowValOneVertical && rowValOneVertical == rowValTwoVertical && rowValTwoVertical == rowValThreeVertical && rowValThreeVertical == rowValFourVertical) {
                    winningPieces = [[j, i], [j + 1, i], [j + 2, i], [j + 3, i]]
                    return 1
                }
                if (playerPiece == rowValOneVertical && rowValOneVertical == rowValTwoVertical && rowValTwoVertical == rowValThreeVertical && rowValThreeVertical == rowValFourVertical) {
                    winningPieces = [[j, i], [j + 1, i], [j + 2, i], [j + 3, i]]
                    return -1
                }
            }

            if (j == 0 && i < 4) {

                let IJvalues = null

                if (i == 0) {
                    IJvalues = [[0, 0]]
                }
                else {
                    IJvalues = [[i, 0], [0, i]]
                }

                for (const [iValue, jValue] of IJvalues) {

                    let tempIValue = (board.length - 1) - iValue

                    let xIncrement = 0

                    let yIncrement = 0

                    let z = 0

                    while (z < 3) {

                        try {
                            rowValOneDiagonal = board[iValue + xIncrement][jValue + yIncrement]
                            rowValTwoDiagonal = board[iValue + xIncrement + 1][jValue + yIncrement + 1]
                            rowValThreeDiagonal = board[iValue + xIncrement + 2][jValue + yIncrement + 2]
                            rowValFourDiagonal = board[iValue + xIncrement + 3][jValue + yIncrement + 3]

                            rowValOneDiagonalReverse = board[tempIValue - xIncrement][jValue + yIncrement]
                            rowValTwoDiagonalReverse = board[tempIValue - xIncrement - 1][jValue + yIncrement + 1]
                            rowValThreeDiagonalReverse = board[tempIValue - xIncrement - 2][jValue + yIncrement + 2]
                            rowValFourDiagonalReverse = board[tempIValue - xIncrement - 3][jValue + yIncrement + 3]

                            if (computerPiece == rowValOneDiagonal && rowValOneDiagonal == rowValTwoDiagonal && rowValTwoDiagonal == rowValThreeDiagonal && rowValThreeDiagonal == rowValFourDiagonal) {
                                winningPieces = [[iValue + xIncrement, jValue + yIncrement], [iValue + xIncrement + 1, jValue + yIncrement + 1], [iValue + xIncrement + 2, jValue + yIncrement + 2], [iValue + xIncrement + 3, jValue + yIncrement + 3]]
                                return 1
                            }
                            if (playerPiece == rowValOneDiagonal && rowValOneDiagonal == rowValTwoDiagonal && rowValTwoDiagonal == rowValThreeDiagonal && rowValThreeDiagonal == rowValFourDiagonal) {
                                winningPieces = [[iValue + xIncrement, jValue + yIncrement], [iValue + xIncrement + 1, jValue + yIncrement + 1], [iValue + xIncrement + 2, jValue + yIncrement + 2], [iValue + xIncrement + 3, jValue + yIncrement + 3]]
                                return -1
                            }

                            if (computerPiece == rowValOneDiagonalReverse && rowValOneDiagonalReverse == rowValTwoDiagonalReverse && rowValTwoDiagonalReverse == rowValThreeDiagonalReverse && rowValThreeDiagonalReverse == rowValFourDiagonalReverse) {
                                winningPieces = [[tempIValue - xIncrement, jValue + yIncrement], [tempIValue - xIncrement - 1, jValue + yIncrement + 1], [tempIValue - xIncrement - 2, jValue + yIncrement + 2], [tempIValue - xIncrement - 3, jValue + yIncrement + 3]]
                                return 1
                            }
                            if (playerPiece == rowValOneDiagonalReverse && rowValOneDiagonalReverse == rowValTwoDiagonalReverse && rowValTwoDiagonalReverse == rowValThreeDiagonalReverse && rowValThreeDiagonalReverse == rowValFourDiagonalReverse) {
                                winningPieces = [[tempIValue - xIncrement, jValue + yIncrement], [tempIValue - xIncrement - 1, jValue + yIncrement + 1], [tempIValue - xIncrement - 2, jValue + yIncrement + 2], [tempIValue - xIncrement - 3, jValue + yIncrement + 3]]
                                return -1
                            }
                        }
                        catch (error) {

                        }

                        xIncrement += 1
                        yIncrement += 1

                        z += 1
                    }
                }
            }
        }
    }

    if (totalNonEmptyCount == 42) {
        return 0
    }
    else {
        return "Nf"
    }
}

function checkForWinner() {

    if (currPlayer == "X") {
        gameStatus = checkGameStatus(board)
    }

    if (gameStatus === 1) {
        computerScore += 1
        document.getElementById("computer-score").textContent = computerScore
        gameOver = true
        document.getElementById("winner").append("Computer Won!")
    }
    else if (gameStatus === -1) {
        playerScore += 1
        document.getElementById("player-score").textContent = playerScore
        gameOver = true
        document.getElementById("winner").append("Player Won!")
    }
    else if (gameStatus === 0) {
        gameOver = true
        document.getElementById("winner").append("Tie!")
    }

    if (gameStatus === 1 || gameStatus === -1) {

        prevComputerTile.classList.remove("recent-yellow-piece")

        for (const winningPiece of winningPieces) {
            rowIndexOfWinningPiece = winningPiece[0]
            colIndexOfWinningPiece = winningPiece[1]


            let tile = document.getElementById(rowIndexOfWinningPiece.toString() + "-" + colIndexOfWinningPiece.toString());

            tile.classList.add("winning-piece")
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const restartBtn = document.getElementById('restart-btn')

    restartBtn.addEventListener('click', () => {
        for (let rowIndex = 0; rowIndex < rowLength; rowIndex++) {
            for (let colIndex = 0; colIndex < colLength; colIndex++) {

                if (board[rowIndex][colIndex] != "-") {
                    board[rowIndex][colIndex] = "-"
                }

                let tile = document.getElementById(rowIndex.toString() + "-" + colIndex.toString());
                tile.classList.remove("red-piece");
                tile.classList.remove("yellow-piece");
                tile.classList.remove("winning-piece");
                tile.classList.remove("recent-yellow-piece");
            }
        }

        currColumns = [5, 5, 5, 5, 5, 5, 5]

        document.getElementById("winner").textContent = ""
        colIndex = null
        gameOver = false
        gameStatus = null
        currPlayer = "X"
    })
}
)