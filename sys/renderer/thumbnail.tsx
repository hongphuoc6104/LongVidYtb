import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';

export const Thumbnail: React.FC<any> = ({image, text, width, height}) => (
  <AbsoluteFill style={{background: '#0F172A', width, height}}>
    <Img src={staticFile(image)} decoding="sync" style={{width: '100%', height: '100%', objectFit: height > width ? 'contain' : 'cover'}} />
    <AbsoluteFill style={{background: 'linear-gradient(0deg, #0F172Aee, transparent 80%)'}} />
    <div style={{position: 'absolute', left: '6%', bottom: '20%', width: '78%', fontFamily: 'Arial', fontWeight: 900, fontSize: height > width ? 100 : 130, color: '#FACC15', textShadow: '0 4px 10px #000'}}>{text}</div>
  </AbsoluteFill>
);
