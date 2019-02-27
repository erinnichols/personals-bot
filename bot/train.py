from textgenrnn import textgenrnn


def train(filename, model_name, new_model=True):
    train_config = {
        'rnn_layers': 2,
        'rnn_size': 128,
        'rnn_bidirectional': True,
        'max_words': 10000,
        'dim_embeddings': 100,
        'single_text': False,
        'name': model_name,
        'line_delimited': True,
        'new_model': new_model,
        'num_epochs': 20,
        'train_size': .95,
        'dropout': .05,
    }
    if model_name == 'bodies':
        train_config.update({
            'max_length': 6,
            'word_level': True,
            'num_epochs': 10,
            'max_gen_length': 50
        })
    textgen = textgenrnn(name=model_name)
    textgen.train_from_file(filename, **train_config)


def train_all():
    train('data/headings.txt', 'headings')
    train('data/handles.txt', 'handles')
    train('data/locations.txt', 'locations')
    train('data/bodies.txt', 'bodies')
