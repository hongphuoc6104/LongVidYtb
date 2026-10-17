import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';

export interface ThumbnailProps {
  image: string;
  text: string;
  width?: number;
  height?: number;
}

export const Thumbnail: React.FC<ThumbnailProps> = ({image, text, width = 1920, height = 1080}) => {
  const isHorizontal = width >= height;
  const fontSize = isHorizontal ? Math.round(width * 0.048) : Math.round(width * 0.075);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: '#0F172A',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
      }}
    >
      {image && (
        <Img
          src={staticFile(image)}
          style={{
            position: 'absolute',
            width: '100%',
            height: '100%',
            objectFit: 'cover',
          }}
        />
      )}
      {/* Contrast overlay */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(to top, rgba(15, 23, 42, 0.92) 0%, rgba(15, 23, 42, 0.4) 50%, rgba(15, 23, 42, 0.8) 100%)',
        }}
      />
      {text && (
        <div
          style={{
            position: 'absolute',
            bottom: isHorizontal ? '14%' : '20%',
            left: '8%',
            right: '8%',
            textAlign: 'center',
            color: '#FACC15',
            fontSize,
            fontWeight: 900,
            lineHeight: 1.25,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            textShadow: '0 6px 24px rgba(0, 0, 0, 0.95), 0 2px 8px rgba(0, 0, 0, 0.8)',
          }}
        >
          {text}
        </div>
      )}
    </AbsoluteFill>
  );
};
