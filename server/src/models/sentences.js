import mongoose from 'mongoose';


const scheme = new mongoose.Schema({
	type: {type: String, required: true},
	sentences: {type: [String], required: true}
})

const Sentences = mongoose.model('Sentences', scheme, 'Sentences');


export default Sentences;