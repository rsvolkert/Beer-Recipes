import numpy as np
import pandas as pd
import tensorflow as tf

recipes = pd.read_csv('Data/recipes.csv')
instructions = [recipe for recipe in recipes['recipe']]

MAX_LEN = max([len(instruction) for instruction in instructions])

STOP = '#'
STOP_NAME = 'NAME'
STOP_STYLE = 'STYLE'
STOP_METHOD = 'METHOD'
STOP_INGREDIENTS = 'INGREDIENTS'
STOP_INSTRUCTIONS = 'INSTRUCTIONS'

tokenizer = tf.keras.preprocessing.text.Tokenizer(
    char_level=True,
    filters='',
    lower=False,
    split=''
)

tokenizer.fit_on_texts([STOP])
tokenizer.fit_on_texts(instructions)

VOCABULARY_SIZE = len(tokenizer.word_counts) + 1

vectorized = tokenizer.texts_to_sequences(instructions)
vectorized_padded_without_stops = tf.keras.preprocessing.sequence.pad_sequences(
    vectorized,
    padding='post',
    truncating='post',
    value=tokenizer.texts_to_sequences([STOP])[0]
)
vectorized_padded = tf.keras.preprocessing.sequence.pad_sequences(
    vectorized_padded_without_stops,
    padding='post',
    truncating='post',
    value=tokenizer.texts_to_sequences([STOP])[0]
)

MAX_LEN = len(vectorized_padded[0])

# Define loss function for reloading model
def loss(labels, logits):
    entropy = tf.keras.losses.sparse_categorical_crossentropy(
        y_true=labels,
        y_pred=logits,
        from_logits=True
    )
    
    return entropy

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.models.Sequential()
    
    model.add(tf.keras.layers.Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        batch_input_shape=[batch_size, None]
    ))
    
    model.add(tf.keras.layers.LSTM(
        units=rnn_units,
        return_sequences=True,
        stateful=True,
        recurrent_initializer=tf.keras.initializers.GlorotNormal()
    ))
    
    model.add(tf.keras.layers.Dense(vocab_size))
    
    return model

model = tf.keras.models.load_model('model.h5', custom_objects={'loss' : loss})

simple_size = 1

simplified = build_model(
    vocab_size=VOCABULARY_SIZE,
    embedding_dim=256,
    rnn_units=1024,
    batch_size=simple_size
)
simplified.set_weights(model.get_weights())
simplified.build(tf.TensorShape([simple_size, None]))

simplified.summary()

def generate_recipe(model, NAME, STYLE, METHOD, num_generate=1000, temperature=1.0):
  padded_start_string = f"""{STOP_NAME}
{NAME}

{STOP_STYLE}
{STYLE}

{STOP_METHOD}
{METHOD} 

INGREDIENTS

    FERMENTABLES 
"""

  indicies = np.array(tokenizer.texts_to_sequences([padded_start_string]))
  text_generated = []

  model.reset_states()
  for char_idx in range(num_generate):
    predictions = tf.squeeze(model(indicies), 0) / temperature

    predicted_id = tf.random.categorical(
        predictions,
        num_samples=1
    )[-1,0].numpy()

    indicies = tf.expand_dims([predicted_id], 0)

    next_character = tokenizer.sequences_to_texts(indicies.numpy())[0]
    text_generated.append(next_character)

  return padded_start_string + ''.join(text_generated)

def generate_combos(model, NAME, STYLE, METHOD, temperatures):
  recipe_length = MAX_LEN
  
  for temperature in temperatures:
    generated_recipe = generate_recipe(
        model,
        NAME,
        STYLE,
        METHOD,
        num_generate=recipe_length,
        temperature=temperature
    )
    print(f'Attempt: {NAME} + {temperature}')
    print('---------------------------')
    print(generated_recipe.strip('#'))
    print('###########################\n')    