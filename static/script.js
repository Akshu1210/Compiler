let editor;
let outputArea;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'javascript',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true
    });

    outputArea = document.getElementById('output-area');

    // Run button click handler
    document.getElementById('run-btn').addEventListener('click', runCode);

    // Clear button click handler
    document.getElementById('clear-btn').addEventListener('click', clearOutput);
});

async function runCode() {
    const code = editor.getValue();
    try {
        const response = await fetch('/compile', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });

        const result = await response.json();
        if (result.error) {
            appendOutput('Error: ' + result.error, 'error');
        } else {
            appendOutput('Output: ' + result.output);
        }
    } catch (error) {
        appendOutput('Error: Failed to compile code', 'error');
    }
}

function appendOutput(text, type = 'success') {
    const line = document.createElement('div');
    line.textContent = text;
    line.className = type;
    outputArea.appendChild(line);
    outputArea.scrollTop = outputArea.scrollHeight;
}

function clearOutput() {
    outputArea.innerHTML = '';
}

const examples = {
    arithmetic: `// Arithmetic operations
2 + 3 * 4;
10 - 5 / 2;
(15 + 5) * 2;`,

    variables: `// Variable assignments
x = 5;
y = 10;
print x + y;
z = (x + y) * 2;
print z;`,

    expressions: `// Complex expressions
a = 15;
b = 3;
print (a + b) * (a - b);
print a * b + b * b;`
};

function loadExample(type) {
    editor.setValue(examples[type]);
} 